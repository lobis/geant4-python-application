"""Hand results from the Geant4 child process to the parent.

Pickling a run's awkward arrays through ``multiprocessing.Pipe`` runs at
~60-80 MB/s on macOS, which made it most of ``Application.run``'s wall time.
Large results go through one POSIX shared-memory block instead: the child
writes the arrays' raw buffers (``ak.to_buffers``) into it and sends only the
forms, lengths and buffer offsets through the pipe. The parent unlinks the
block, copies it out and rebuilds the arrays with ``ak.from_buffers``.

Small results, results without awkward arrays, and results whose block can't
be allocated are pickled through the pipe as before.

Cleanup: the parent chooses each block's name (``block_name``), so it can
unlink the block itself when the child dies mid-transfer. The child unlinks the
block if anything fails before the descriptor is sent, and the parent unlinks
it as soon as it has attached. Should both processes crash, multiprocessing's
resource tracker, which they share, unlinks it once they have exited.

Environment variables, read by the child when it packs a result:

``GEANT4_PYTHON_APPLICATION_SHM_MIN_BYTES``
    Results with fewer bytes of array data go through the pipe (default
    1 MiB). ``0`` sends every array result through shared memory; a huge value
    disables shared memory.
``GEANT4_PYTHON_APPLICATION_SHM_TEST_PAUSE``
    Testing only: seconds to sleep after writing a block, before sending it.
"""

from __future__ import annotations

import os
import sys
import time
from multiprocessing import shared_memory

import awkward as ak
import numpy as np

# Below this many bytes of array data the pipe is as fast and needs no cleanup.
MIN_SHARED_BYTES = 1 << 20
MIN_BYTES_VARIABLE = "GEANT4_PYTHON_APPLICATION_SHM_MIN_BYTES"
TEST_PAUSE_VARIABLE = "GEANT4_PYTHON_APPLICATION_SHM_TEST_PAUSE"
_ALIGNMENT = 64
_BUFFER_KEY = "{form_key}-{attribute}"
_BYTEORDER = "<" if sys.byteorder == "little" else ">"

# Parent side: how many results holding awkward arrays arrived by each path.
stats = {"shared_memory": 0, "pipe": 0}


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


def block_name(prefix: str, counter: int) -> str:
    """Name of the block for message ``counter`` (macOS allows 30 characters)."""
    return f"{prefix}_{counter:x}"


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


def _min_bytes() -> int:
    try:
        return int(os.environ[MIN_BYTES_VARIABLE])
    except (KeyError, ValueError):
        return MIN_SHARED_BYTES


def _allocate(size: int, name: str | None = None) -> shared_memory.SharedMemory:
    block = shared_memory.SharedMemory(name=name, create=True, size=size)
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


def destroy(name: str) -> None:
    """Unlink the block called name, if it exists."""
    try:
        block = shared_memory.SharedMemory(name=name)
    except FileNotFoundError:
        return
    block.close()
    block.unlink()


def pack(result, name: str | None = None, min_bytes: int | None = None):
    """Child side: the object to send through the pipe in place of result."""
    if min_bytes is None:
        min_bytes = _min_bytes()
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

        block = _allocate(size, name)
    except Exception:
        return result

    try:
        _write(block, size, flattened.values())

        def to_shared(array):
            _, form, length, buffers = flattened[id(array)]
            attrs = getattr(array, "attrs", None)
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

    pause = os.environ.get(TEST_PAUSE_VARIABLE)
    if pause:
        time.sleep(float(pause))
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
    """Free the block of a packed result that won't be unpacked."""
    if isinstance(message, SharedResult):
        destroy(message.name)


def unpack(message):
    """Parent side: the result that pack(result) stood in for."""
    if not isinstance(message, SharedResult):
        if _arrays(message):
            stats["pipe"] += 1
        return message

    try:
        block = shared_memory.SharedMemory(name=message.name)
    except FileNotFoundError:
        msg = f"Shared memory block {message.name} holding the result is gone"
        raise RuntimeError(msg) from None
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
        kwargs = {} if shared.attrs is None else {"attrs": shared.attrs}
        return ak.from_buffers(
            shared.form,
            shared.length,
            container,
            buffer_key=_BUFFER_KEY,
            byteorder=_BYTEORDER,
            behavior=shared.behavior,
            **kwargs,
        )

    result = _replace_shared(message.payload, from_shared)
    stats["shared_memory"] += 1
    return result


def _replace_shared(obj, function):
    if isinstance(obj, SharedArray):
        return function(obj)
    if type(obj) is dict:
        return {key: _replace_shared(value, function) for key, value in obj.items()}
    if type(obj) in (list, tuple):
        return type(obj)(_replace_shared(value, function) for value in obj)
    return obj
