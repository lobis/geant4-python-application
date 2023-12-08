from __future__ import annotations

import numpy as np
import pytest
import requests

from geant4_python_application import Application, basic_gdml


def test_missing_setup():
    app = Application()

    with pytest.raises(RuntimeError):
        app.initialize()


def test_missing_manager():
    app = Application()

    with pytest.raises(RuntimeError):
        app.setup_detector(gdml="")


def test_run():
    app = Application()

    app.setup_manager().setup_detector(gdml=basic_gdml).setup_physics().setup_action()
    app.initialize()
    events = app.run(100)
    assert len(events) == 100


def test_multiple_apps():
    apps = [Application() for _ in range(10)]

    for app in apps:
        app.setup_manager().setup_detector(
            gdml=basic_gdml
        ).setup_physics().setup_action()

    for app in apps:
        app.initialize()

    for app in apps:
        events = app.run(10)
        assert len(events) == 10


def test_seed_single_thread():
    app = Application()

    app.setup_manager()
    app.seed = 1100
    app.setup_physics()
    app.setup_detector(gdml=basic_gdml)
    app.setup_action()

    app.initialize()

    assert app.seed == 1100

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
    energy = np.array(events["track.step.energy"][0][0][0:5])
    assert np.allclose(energy, reference_value, atol=1e-5)


def test_event_data_is_cleared():
    app = Application()

    app.setup_manager().setup_physics()
    app.setup_detector(gdml=basic_gdml)
    app.setup_action()

    app.initialize()

    for _ in range(10):
        events = app.run(100)
        assert len(events) == 100


# raising the number of threads to a high value (e.g. 1000) has a very low chance to cause a segfault. TODO: investigate
@pytest.mark.parametrize("n_threads", [0, 1, 2, 20])
def test_complex_gdml(n_threads):
    url = "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"

    app = Application()
    app.setup_manager(n_threads=n_threads).setup_physics().setup_detector(
        gdml=requests.get(url).text
    ).setup_action()

    app.detector.sensitive_volumes = {"gasVolume"}

    app.initialize()

    app.command("/gun/particle neutron")
    app.command("/gun/energy 100 MeV")
    app.command("/gun/direction 0 0 -1")
    app.command("/gun/position 0 0 10 m")

    assert len(app.detector.logical_volumes) == 22
    assert len(app.detector.physical_volumes) == 309

    events = app.run(1000)
