from __future__ import annotations

import pickle
from multiprocessing import shared_memory

import awkward as ak
import numpy as np
import pytest

from geant4_python_application import Application, _transfer, basic_gdml


def _block_exists(name: str) -> bool:
    try:
        block = shared_memory.SharedMemory(name=name)
    except FileNotFoundError:
        return False
    block.close()
    return True


def _thread_result(n: int) -> dict:
    return {
        "id": ak.Array(np.arange(n, dtype=np.int64)),
        "track_particle": ak.Array([["e-", "gamma"][: i % 3] for i in range(n)]),
        "step_position": ak.Array(
            [[[{"x": 1.0 * i, "y": 2.0, "z": 3.0}] * (i % 4)] for i in range(n)]
        ),
        "maybe": ak.Array([None if i % 2 else i for i in range(n)]),
        "point": ak.Array([{"x": 1.0 * i} for i in range(n)], with_name="Point"),
    }


def test_large_result_goes_through_shared_memory():
    result = [_thread_result(50_000), _thread_result(7)]
    packed = _transfer.pack(result, min_bytes=0)
    assert isinstance(packed, _transfer.SharedResult)
    assert len(pickle.dumps(packed)) < 10_000
    assert _block_exists(packed.name)

    unpacked = _transfer.unpack(pickle.loads(pickle.dumps(packed)))
    assert not _block_exists(packed.name)
    assert isinstance(unpacked, list)
    for original, copy in zip(result, unpacked):
        assert original.keys() == copy.keys()
        for key in original:
            assert copy[key].type == original[key].type
            assert ak.array_equal(copy[key], original[key])


def test_small_and_non_array_results_are_pickled():
    small = {"id": ak.Array([1, 2, 3])}
    assert _transfer.pack(small) is small
    for value in (None, 3, "text", {"a"}, [1, 2], ValueError("x")):
        assert _transfer.pack(value, min_bytes=0) is value
        assert _transfer.unpack(value) is value


def test_discard_unlinks_block():
    packed = _transfer.pack(_thread_result(100), min_bytes=0)
    assert _block_exists(packed.name)
    _transfer.discard(packed)
    assert not _block_exists(packed.name)
    with pytest.raises(RuntimeError, match="gone"):
        _transfer.unpack(packed)


def test_allocation_failure_falls_back_to_pickle(monkeypatch):
    def fail(size):
        raise OSError("no space")

    monkeypatch.setattr(_transfer, "_allocate", fail)
    result = {"id": ak.Array(np.arange(1000))}
    assert _transfer.pack(result, min_bytes=0) is result


def test_run_results_match_across_thread_counts():
    # Large enough that every run goes through shared memory.
    commands = ["/gun/particle e-", "/gun/energy 1 GeV"]
    for n_threads in (0, 2):
        with Application(gdml=basic_gdml, n_threads=n_threads, seed=1) as app:
            app.commands(commands)
            events = app.run(100)
            assert len(events) == 100
            assert ak.all(events.id == np.arange(100))
            assert events.layout.nbytes > _transfer.MIN_SHARED_BYTES
