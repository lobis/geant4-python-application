from __future__ import annotations

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


def test_seed_single_thread():
    with Application(gdml=basic_gdml, seed=1100) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 100 cm")

        # launch 100 events
        events = app.run(100)
        assert len(events) == 100
        reference_value = [
            0.00000000e00,
            4.54930276e-01,
            2.25814551e-01,
            8.09506886e-03,
            1.22345221e00,
        ]
        energy = np.array(events.track.step.energy[0][0][0:5])
        assert np.allclose(energy, reference_value, atol=1e-5)
        assert app.seed == 1100


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


# raising the number of threads to a high value (e.g. 1000) has a very low chance to cause a segfault. TODO: investigate
@pytest.mark.parametrize("n_threads", [0, 1, 2, 20])
def test_complex_gdml(n_threads):
    with Application(gdml=complex_gdml) as app:
        app.detector.sensitive_volumes = {"gasVolume"}

        app.initialize()

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 10 m")

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
        assert len(fields) == 24
        app.set_event_fields(fields)

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 10 m")

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
