from __future__ import annotations

import awkward as ak
import numpy as np
import pytest
import requests

from geant4_python_application import Application, basic_gdml

complex_gdml = requests.get(
    "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"
).text


def test_missing_setup():
    app = Application()
    app.start(setup=False)
    with pytest.raises(RuntimeError):
        app.initialize()


def test_missing_manager():
    app = Application()
    app.start(setup=False)
    with pytest.raises(RuntimeError):
        app.setup_detector(gdml="")


def test_no_initialize():
    app = Application()
    with pytest.raises(RuntimeError):
        app.setup_manager()


def test_run():
    with Application(gdml=basic_gdml) as app:
        events = app.run(100)
        assert len(events) == 100


def test_reference_physics_list():
    assert "custom" in Application.available_physics_lists()
    assert "FTFP_BERT" in Application.available_physics_lists()
    with Application(gdml=basic_gdml, physics="FTFP_BERT") as app:
        assert len(app.run(1)) == 1


def test_optical_physics_and_magnetic_field():
    with Application(gdml=basic_gdml, optical=True) as app:
        app.detector.magnetic_field = (0.0, 0.0, 1.5)
        assert app.detector.magnetic_field == (0.0, 0.0, 1.5)
        assert len(app.run(1)) == 1


def _seeded_step_energies(seed):
    with Application(gdml=basic_gdml, seed=seed) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 45 cm")

        # launch 100 events
        events = app.run(100)
        assert len(events) == 100
        assert app.seed == seed
        return np.asarray(ak.flatten(events.track.step.energy, axis=None))


def test_seed_single_thread():
    # Exact values change with the Geant4 version, so check reproducibility instead.
    first = _seeded_step_energies(1100)
    assert len(first) > 0
    assert np.array_equal(first, _seeded_step_energies(1100))
    other = _seeded_step_energies(1101)
    assert len(first) != len(other) or not np.array_equal(first, other)


def test_multiple_apps():
    apps = [Application(gdml=basic_gdml) for _ in range(10)]

    for app in apps:
        app.start()

    for app in apps:
        events = app.run(10)
        assert len(events) == 10

    for app in apps:
        app.stop()


def test_event_data_is_cleared():
    with Application(gdml=basic_gdml) as app:
        for _ in range(10):
            events = app.run(100)
            assert len(events) == 100


@pytest.mark.parametrize("n_threads", [0, 1, 4])
def test_complex_gdml(n_threads):
    if n_threads > 0 and not Application.multithreading_available():
        pytest.skip("linked Geant4 runtime was built without multithreading")
    with Application(gdml=complex_gdml, n_threads=n_threads) as app:
        app.detector.sensitive_volumes = {"gasVolume"}

        app.initialize()

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 1.4 m")

        assert len(app.detector.logical_volumes) == 22
        assert len(app.detector.physical_volumes) == 309

        events = app.run(1000)


def test_python_thread_safety():
    import concurrent.futures

    with Application(gdml=basic_gdml) as app:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(app.run, 10) for _ in range(10)]
            for future in futures:
                future.result()


def test_fields():
    with Application(gdml=complex_gdml, seed=1000) as app:
        app.detector.sensitive_volumes = {"gasVolume"}

        fields = app.get_event_fields_complete()
        assert len(fields) == 25
        app.set_event_fields(fields)

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 1.4 m")

        events = app.run(100)


def test_no_step_fields():
    with Application(gdml=basic_gdml) as app:
        app.set_event_fields({"id", "track_id"})

        events = app.run(100)
        assert len(events) == 100
        assert set(events.fields) == {"id", "track"}
        assert set(events.track.fields) == {"id"}


def test_no_track_step_fields():
    with Application(gdml=basic_gdml) as app:
        app.set_event_fields({"id"})

        events = app.run(100)
        assert len(events) == 100
        assert set(events.fields) == {"id"}


def test_no_track_fields():
    with Application(gdml=basic_gdml) as app:
        app.set_event_fields({"id", "step_energy"})

        events = app.run(100)
        assert len(events) == 100
        assert set(events.fields) == {"id", "track"}
        assert set(events.track.fields) == {"step"}
        assert set(events.track.step.fields) == {"energy"}


@pytest.mark.parametrize("initialize_first", [False, True])
def test_primary_outside_world_is_an_error(initialize_first):
    # basic_gdml's world spans +-50 cm; Geant4 11.4 would otherwise crash (or,
    # after initialization, silently keep the previous gun position).
    with Application(gdml=basic_gdml) as app:
        if initialize_first:
            app.initialize()
        app.command("/gun/particle e-")
        app.command("/gun/position 0 0 1 m")
        with pytest.raises(RuntimeError, match="outside the world"):
            app.run(1)
        # the application survives and keeps working
        app.command("/gun/position 0 0 0 cm")
        assert len(app.run(2)) == 2
