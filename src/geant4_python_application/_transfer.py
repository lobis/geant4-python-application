"""Hand results from the Geant4 child process to the parent.

Pickling a run's awkward arrays through ``multiprocessing.Pipe`` runs at
~60-80 MB/s on macOS, which made it most of ``Application.run``'s wall time.
Large results go through one POSIX shared-memory block instead: the child
writes the arrays' raw buffers (``ak.to_buffers``) into it and sends only the
forms, lengths and buffer offsets through the pipe. The parent unlinks the
block, copies it out and rebuilds the arrays with ``ak.from_buffers``.

Small results, results without awkward arrays, and results whose block can't
be allocated are pickled through the pipe as before.

Cleanup: the child unlinks the block if anything fails before the descriptor
is sent, and the parent unlinks it as soon as it has attached. A block left
behind by a process that crashed in between is unlinked by multiprocessing's
resource tracker, which the parent and child share, once both have exited.
"""

from __future__ import annotations

import os
import sys
from multiprocessing import shared_memory

import awkward as ak
import numpy as np

# Below this many bytes of array data the pipe is as fast and needs no cleanup.
MIN_SHARED_BYTES = 1 << 20
_ALIGNMENT = 64
_BUFFER_KEY = "{form_key}-{attribute}"
_BYTEORDER = "<" if sys.byteorder == "little" else ">"


class SharedArray:
    """Stands in for an ``ak.Array`` whose buffers are in a ``SharedResult`` block."""

    __slots__ = ("attrs", "behavior", "buffers", "form", "length")

    def __init__(self, form, length, buffers, behavior, attrs):
        self.form = form
        self.length = length
        self.buffers = buffers  # buffer key -> (offset, nbytes)
        self.behavior = behavior
        self.attrs = attrs

    def __getstate__(self):
        return {name: getattr(self, name) for name in self.__slots__}

    def __setstate__(self, state):
        for name, value in state.items():
            setattr(self, name, value)


class SharedResult:
    """What goes through the pipe instead of a large result."""

    __slots__ = ("name", "payload", "size")

    def __init__(self, name: str, size: int, payload):
        self.name = name
        self.size = size
        # The result with every ak.Array replaced by a SharedArray.
        self.payload = payload

    def __getstate__(self):
        return {name: getattr(self, name) for name in self.__slots__}

    def __setstate__(self, state):
        for name, value in state.items():
            setattr(self, name, value)


def _map_arrays(obj, function):
    """Copy of nested dicts/lists/tuples with each ak.Array replaced by function(array)."""
    if isinstance(obj, ak.Array):
        return function(obj)
    if type(obj) is dict:
        return {key: _map_arrays(value, function) for key, value in obj.items()}
    if type(obj) in (list, tuple):
        return type(obj)(_map_arrays(value, function) for value in obj)
    return obj


def _arrays(obj):
    found = []
    _map_arrays(obj, found.append)
    return found


def _allocate(size: int) -> shared_memory.SharedMemory:
    block = shared_memory.SharedMemory(create=True, size=size)
    if sys.platform.startswith("linux"):
        # /dev/shm is a tmpfs that can be smaller than the result (64 MB in
        # Docker by default). Writing past its limit raises SIGBUS and kills
        # the process, so reserve the pages now and fall back if they don't fit.
        try:
            os.posix_fallocate(block._fd, 0, size)
        except BaseException:
            block.close()
            block.unlink()
            raise
    return block


def _destroy(name: str) -> None:
    try:
        block = shared_memory.SharedMemory(name=name)
    except FileNotFoundError:
        return
    block.close()
    block.unlink()


def pack(result, min_bytes: int = MIN_SHARED_BYTES):
    """Child side: the object to send through the pipe in place of result."""
    arrays = _arrays(result)
    if not arrays or sum(array.layout.nbytes for array in arrays) < min_bytes:
        return result

    try:
        flattened = {}
        offset = 0
        for array in arrays:
            if id(array) in flattened:
                continue
            form, length, container = ak.to_buffers(
                ak.to_packed(array, highlevel=False),
                buffer_key=_BUFFER_KEY,
                form_key="node{id}",
                byteorder=_BYTEORDER,
            )
            buffers = {}
            for key, values in container.items():
                raw = np.ascontiguousarray(values).reshape(-1).view(np.uint8)
                buffers[key] = (offset, raw)
                offset += -(-raw.nbytes // _ALIGNMENT) * _ALIGNMENT
            flattened[id(array)] = (array, form, length, buffers)
        size = max(offset, 1)

        block = _allocate(size)
    except Exception:
        return result

    try:
        _write(block, size, flattened.values())

        def to_shared(array):
            _, form, length, buffers = flattened[id(array)]
            attrs = array.attrs
            if attrs is not None:
                attrs = {k: v for k, v in attrs.items() if not k.startswith("@")}
            return SharedArray(
                form,
                length,
                {
                    key: (start, buffer.nbytes)
                    for key, (start, buffer) in buffers.items()
                },
                None if array.behavior is ak.behavior else array.behavior,
                attrs,
            )

        packed = SharedResult(block.name, size, _map_arrays(result, to_shared))
    except BaseException as error:
        block.close()
        block.unlink()
        if isinstance(error, Exception):
            return result
        raise
    block.close()
    return packed


def _write(block, size, flattened) -> None:
    data = np.ndarray((size,), dtype=np.uint8, buffer=block.buf)
    try:
        for _, _, _, buffers in flattened:
            for start, buffer in buffers.values():
                data[start : start + buffer.nbytes] = buffer
    finally:
        # block.close() refuses while a view of its buffer is alive.
        del data


def discard(message) -> None:
    """Child side: free the block of a packed result that could not be sent."""
    if isinstance(message, SharedResult):
        _destroy(message.name)


def unpack(message):
    """Parent side: the result that pack(result) stood in for."""
    if not isinstance(message, SharedResult):
        return message

    try:
        block = shared_memory.SharedMemory(name=message.name)
    except FileNotFoundError:
        raise RuntimeError(
            f"Shared memory block {message.name} holding the result is gone"
        ) from None
    try:
        # Unlinking first means nothing is left behind if the copy is interrupted;
        # the mapping stays valid until close().
        block.unlink()
        data = np.empty(message.size, dtype=np.uint8)
        data[:] = np.ndarray((message.size,), dtype=np.uint8, buffer=block.buf)
    finally:
        block.close()

    def from_shared(shared):
        container = {
            key: data[start : start + nbytes]
            for key, (start, nbytes) in shared.buffers.items()
        }
        return ak.from_buffers(
            shared.form,
            shared.length,
            container,
            buffer_key=_BUFFER_KEY,
            byteorder=_BYTEORDER,
            behavior=shared.behavior,
            attrs=shared.attrs,
        )

    return _replace_shared(message.payload, from_shared)


def _replace_shared(obj, function):
    if isinstance(obj, SharedArray):
        return function(obj)
    if type(obj) is dict:
        return {key: _replace_shared(value, function) for key, value in obj.items()}
    if type(obj) in (list, tuple):
        return type(obj)(_replace_shared(value, function) for value in obj)
    return obj
