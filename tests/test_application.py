from __future__ import annotations

import numpy as np
import pytest

import geant4_python_application
from geant4_python_application import Application, basic_gdml


def test_imports():
    assert Application
    assert geant4_python_application
    assert geant4_python_application.Application
    assert geant4_python_application.PrimaryGeneratorAction
    assert geant4_python_application.StackingAction
    assert geant4_python_application.__doc__
    assert geant4_python_application.__version__


def test_setup_and_run():
    app = geant4_python_application.Application()
    app.setup_manager()
    app.setup_detector(gdml=basic_gdml)
    app.setup_physics()
    app.setup_action()
    app.initialize()
    events = app.run(100)
    assert len(events) == 100


def test_missing_setup():
    app = geant4_python_application.Application()

    with pytest.raises(RuntimeError):
        app.initialize()


def test_missing_manager():
    app = geant4_python_application.Application()

    with pytest.raises(RuntimeError):
        app.setup_detector(gdml="")
        app.setup_detector()


@pytest.mark.skip(reason="Fix segfault")
def test_multiple_apps():
    # Could this work somehow?
    with pytest.raises(RuntimeError):
        for _ in range(10):
            app = geant4_python_application.Application()
            app.setup_manager()
            app.setup_detector()
            app.setup_physics()
            app.setup_action()
            app.initialize()
            app.run()


@pytest.mark.skip(reason="Fix segfault")
def test_seed_single_thread():
    app = geant4_python_application.Application()

    app.setup_manager()
    app.random_seed = 137
    app.setup_physics()
    app.setup_detector()
    app.setup_action()

    app.initialize()

    assert app.random_seed == 137

    # launch 100 events
    events = app.run(100)
    assert len(events) == 100

    reference_value = [
        0.0,
        231.04991,
        164.29599,
        72.8029,
        66.77133,
        57.87128,
        42.725155,
        44.92826,
        57.972427,
        31.946453,
        31.096113,
        37.32029,
        14.65972,
        23.0362,
        47.28438,
        14.196298,
        19.810057,
        13.936412,
        17.764618,
        10.532204,
    ]

    energy = np.array(events["track.step.energy"][0][0])
    assert np.allclose(energy, reference_value, atol=1e-5)


@pytest.mark.skip(reason="Fix segfault")
def test_event_data_is_cleared():
    app = geant4_python_application.Application()

    app.setup_manager()
    app.setup_physics()
    app.setup_detector()
    app.setup_action()

    app.initialize()

    for _ in range(10):
        events = app.run(100)
        assert len(events) == 100
