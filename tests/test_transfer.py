from __future__ import annotations

import os
import pickle
import signal
import sys
import threading
import time
from multiprocessing import shared_memory
from pathlib import Path

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
    def fail(*_):
        msg = "no space"
        raise OSError(msg)

    monkeypatch.setattr(_transfer, "_allocate", fail)
    result = {"id": ak.Array(np.arange(1000))}
    assert _transfer.pack(result, min_bytes=0) is result


def test_unpack_failure_still_unlinks_block():
    packed = _transfer.pack(_thread_result(100), min_bytes=0)
    for shared in packed.payload.values():
        shared.length += 10**6  # buffers too short: from_buffers raises
    with pytest.raises(Exception):  # noqa: B017, PT011
        _transfer.unpack(packed)
    assert not _block_exists(packed.name)


# -- through the Geant4 child process ------------------------------------------

# 1 GeV e- into ~20 X0 of PbWO4: ~4 MB of default event fields per event.
PBWO4_GDML = """<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
    <solids>
        <box name="WorldSolid" x="600" y="600" z="600" lunit="mm"/>
        <box name="CaloSolid" x="300" y="300" z="178" lunit="mm"/>
    </solids>
    <structure>
        <volume name="CaloVolume">
            <materialref ref="G4_PbWO4"/>
            <solidref ref="CaloSolid"/>
        </volume>
        <volume name="World">
            <materialref ref="G4_Galactic"/>
            <solidref ref="WorldSolid"/>
            <physvol name="Calo">
                <volumeref ref="CaloVolume"/>
                <position name="CaloPosition" x="0" y="0" z="89" unit="mm"/>
            </physvol>
        </volume>
    </structure>
    <setup name="Default" version="1.0">
        <world ref="World"/>
    </setup>
</gdml>
"""
ELECTRON_COMMANDS = ["/gun/particle e-", "/gun/energy 1 GeV"]
CALO_COMMANDS = [*ELECTRON_COMMANDS, "/gun/position 0 0 -10 mm", "/gun/direction 0 0 1"]

DEV_SHM = Path("/dev/shm")


def _dev_shm_blocks() -> set[str] | None:
    """Blocks made by this package or by SharedMemory's defaults (Linux only)."""
    if not sys.platform.startswith("linux") or not DEV_SHM.is_dir():
        return None
    return {p.name for p in DEV_SHM.iterdir() if p.name.startswith(("psm_", "g4"))}


def _next_block(app: Application) -> str:
    return _transfer.block_name(app._block_prefix, app._message_counter)


@pytest.fixture
def no_leaks():
    """Fails the test if it leaves blocks in /dev/shm (checked on Linux)."""
    before = _dev_shm_blocks()
    yield
    after = _dev_shm_blocks()
    if before is not None:
        assert after - before == set()


def test_large_result_uses_shared_memory_small_uses_pipe(no_leaks):
    with Application(gdml=basic_gdml, seed=1) as app:
        app.commands(ELECTRON_COMMANDS)
        before = dict(_transfer.stats)
        name = _next_block(app)
        events = app.run(100)
        assert events.layout.nbytes > _transfer.MIN_SHARED_BYTES
        assert _transfer.stats["shared_memory"] == before["shared_memory"] + 1
        assert not _block_exists(name)

        before = dict(_transfer.stats)
        events = app.run(1)
        assert events.layout.nbytes < _transfer.MIN_SHARED_BYTES
        assert _transfer.stats["pipe"] == before["pipe"] + 1
        assert _transfer.stats["shared_memory"] == before["shared_memory"]


def _seeded_events(monkeypatch, min_bytes: int):
    monkeypatch.setenv(_transfer.MIN_BYTES_VARIABLE, str(min_bytes))
    with Application(gdml=basic_gdml, seed=1234) as app:
        app.commands(ELECTRON_COMMANDS)
        before = dict(_transfer.stats)
        events = app.run(30)
        used = {k: _transfer.stats[k] - before[k] for k in before}
    return events, used


def test_shared_memory_and_pipe_give_identical_arrays(monkeypatch, no_leaks):
    shared, used_shared = _seeded_events(monkeypatch, 0)
    piped, used_pipe = _seeded_events(monkeypatch, 10**15)
    assert used_shared == {"shared_memory": 1, "pipe": 0}
    assert used_pipe == {"shared_memory": 0, "pipe": 1}

    assert shared.fields == piped.fields
    assert shared.track.fields == piped.track.fields
    assert shared.track.step.fields == piped.track.step.fields
    assert str(shared.type) == str(piped.type)  # nesting, dtypes and record names
    assert ak.array_equal(shared, piped, dtype_exact=True, check_parameters=True)
    assert ak.sum(ak.num(shared.track.step.energy, axis=2)) > 0


def test_no_blocks_left_after_a_run_that_raises(no_leaks):
    with Application(gdml=basic_gdml) as app:
        app.commands(ELECTRON_COMMANDS)
        app.run(100)  # through shared memory
        app.command("/gun/position 0 0 1 m")
        name = _next_block(app)
        with pytest.raises(RuntimeError, match="outside the world"):
            app.run(100)
        assert not _block_exists(name)
        app.command("/gun/position 0 0 0 cm")
        assert len(app.run(100)) == 100


def test_no_blocks_left_when_child_is_killed_mid_transfer(monkeypatch, no_leaks):
    # The child sleeps after writing the block, before sending its descriptor.
    monkeypatch.setenv(_transfer.TEST_PAUSE_VARIABLE, "60")
    app = Application(gdml=basic_gdml)
    app.start()
    app.commands(ELECTRON_COMMANDS)
    name = _next_block(app)
    errors = []

    def run():
        try:
            app.run(100)
        except RuntimeError as error:
            errors.append(error)

    thread = threading.Thread(target=run)
    thread.start()
    deadline = time.monotonic() + 120
    while not _block_exists(name):
        assert time.monotonic() < deadline, "block was never written"
        assert thread.is_alive(), "run returned before writing a block"
        time.sleep(0.05)

    os.kill(app._process.pid, signal.SIGKILL)
    thread.join(30)
    assert not thread.is_alive()
    assert len(errors) == 1
    assert "died" in str(errors[0])
    assert not _block_exists(name)


@pytest.mark.slow
@pytest.mark.skipif(
    not sys.platform.startswith("linux")
    or not DEV_SHM.is_dir()
    or os.statvfs(DEV_SHM).f_blocks * os.statvfs(DEV_SHM).f_frsize > 128 * 2**20,
    reason="needs a Linux /dev/shm of at most 128 MB (e.g. docker --shm-size=64m)",
)
def test_result_larger_than_dev_shm_falls_back_to_pipe(no_leaks):
    shm_bytes = os.statvfs(DEV_SHM).f_blocks * os.statvfs(DEV_SHM).f_frsize
    with Application(gdml=PBWO4_GDML, n_threads=8, seed=1) as app:
        app.commands(CALO_COMMANDS)
        before = dict(_transfer.stats)
        events = app.run(48)
        assert events.layout.nbytes > 1.5 * shm_bytes
        assert _transfer.stats["pipe"] == before["pipe"] + 1
        assert _transfer.stats["shared_memory"] == before["shared_memory"]
        assert len(events) == 48
        assert ak.all(events.id == np.arange(48))
        assert ak.all(ak.num(events.track.id, axis=1) > 100)
        # Smaller results still fit and use shared memory.
        events = app.run(2)
        assert events.layout.nbytes < shm_bytes / 4
        assert _transfer.stats["shared_memory"] == before["shared_memory"] + 1
