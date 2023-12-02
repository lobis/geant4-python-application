from __future__ import annotations

import numpy as np
import pytest
import requests

import geant4_python_application
from geant4_python_application import Application, basic_gdml


def test_imports():
    assert Application
    assert geant4_python_application
    assert geant4_python_application.Application
    assert geant4_python_application.PrimaryGeneratorAction
    assert geant4_python_application.StackingAction


def test_setup_and_run():
    app = Application()

    app.setup_manager().setup_detector(
        gdml=basic_gdml
    ).setup_physics().setup_action().initialize()

    events = app.run(100)
    assert len(events) == 100


def test_missing_setup():
    app = Application()

    with pytest.raises(RuntimeError):
        app.initialize()


def test_missing_manager():
    app = Application()

    with pytest.raises(RuntimeError):
        app.setup_detector(gdml="")
        app.setup_detector()


@pytest.mark.skip(reason="Fix segfault")
def test_multiple_apps():
    # Could this work somehow?
    with pytest.raises(RuntimeError):
        for _ in range(10):
            app = Application()
            app.setup_manager()
            app.setup_detector(gdml=basic_gdml)
            app.setup_physics()
            app.setup_action()
            app.initialize()
            app.run()


@pytest.mark.skip(reason="Fix segfault")
def test_seed_single_thread():
    app = Application()

    app.setup_manager()
    app.random_seed = 137
    app.setup_physics()
    app.setup_detector(gdml=basic_gdml)
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
    app = Application()

    app.setup_manager()
    app.setup_physics()
    app.setup_detector(gdml=basic_gdml)
    app.setup_action()

    app.initialize()

    for _ in range(10):
        events = app.run(100)
        assert len(events) == 100


@pytest.mark.skip(reason="Fix segfault")
def test_complex_gdml():
    url = "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"

    app = Application()

    app.setup_manager()
    app.setup_physics()
    app.setup_detector(gdml=requests.get(url).text)
    app.setup_action()

    app.detector.sensitive_volumes = {"gasVolume"}

    app.initialize()

    # primary generator action can be modified after initialization
    app.generator.set_particle("neutron")
    app.generator.set_energy(100)
    app.generator.set_position((0, 0, 1e3))
    app.generator.set_direction((0, 0, -1))

    assert len(app.detector.logical_volumes) == 22
    assert len(app.detector.physical_volumes) == 309

    events = app.run(1)
    print(events)
