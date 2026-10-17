from __future__ import annotations

import awkward as ak
import numpy as np
import pytest
import requests

from geant4_python_application import Application, basic_gdml

complex_gdml = requests.get(
    "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"
).text


@pytest.mark.parametrize("n_threads", [0, 4])
def test_awkward_primaries(n_threads):
    if n_threads > 0:
        pytest.skip("Not working for MT right now")
    # numpy random seed
    np.random.seed(1234)

    primaries = ak.Array(
        [
            {
                "particle": "geantino",
                "energy": np.random.uniform(1, 1000),
                "direction": {"x": 0, "y": -1, "z": 0},
                "position": {"x": 0, "y": 10, "z": 0},
            }
            for _ in range(100)
        ]
    )
    with Application(gdml=basic_gdml, n_threads=n_threads) as app:
        events = app.run(primaries)
        assert len(events) == len(primaries)

        event_primary_energy = ak.flatten(events.primaries.energy)
        assert np.allclose(event_primary_energy, primaries.energy)


def test_general_particle_source():
    with Application(gdml=basic_gdml) as app:
        app.generator.use_gps().particle("geantino").energy(2, "MeV")
        app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
        events = app.run(2)
        assert len(events) == 2
        assert np.allclose(ak.flatten(events.primaries.energy), 2000)


@pytest.mark.parametrize("initialize_first", [False, True])
def test_generator_multithreaded(initialize_first):
    # In multithreaded mode only the workers have a primary generator; commands
    # issued before they exist are applied once the application is initialized.
    if not Application.multithreading_available():
        pytest.skip("linked Geant4 runtime was built without multithreading")
    with Application(gdml=basic_gdml, n_threads=2, seed=1) as app:
        if initialize_first:
            app.initialize()
        assert app.generator.type == "gun"
        app.generator.particle("proton").energy(50, "MeV")
        app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
        events = app.run(10)
    assert len(events) == 10
    assert set(ak.flatten(events.primaries.particle)) == {"proton"}
    assert np.allclose(ak.flatten(events.primaries.energy), 50000)


def test_general_particle_source_multithreaded():
    if not Application.multithreading_available():
        pytest.skip("linked Geant4 runtime was built without multithreading")
    with Application(gdml=basic_gdml, n_threads=2, seed=1) as app:
        app.generator.use_gps().particle("geantino").energy(2, "MeV")
        app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
        assert app.generator.type == "gps"
        events = app.run(4)
    assert len(events) == 4
    assert set(ak.flatten(events.primaries.particle)) == {"geantino"}
    assert np.allclose(ak.flatten(events.primaries.energy), 2000)


def test_generator_command_typo_multithreaded():
    if not Application.multithreading_available():
        pytest.skip("linked Geant4 runtime was built without multithreading")
    with Application(gdml=basic_gdml, n_threads=2) as app:
        app.command("/gun/energyy 1 MeV")  # kept until the generator exists
        with pytest.raises(RuntimeError, match="/gun/energyy"):
            app.initialize()


def test_multiple_primary_vertices_per_event():
    particle = lambda name, x: {
        "particle": name,
        "energy": 1000.0,
        "direction": {"x": 0.0, "y": 0.0, "z": 1.0},
        "position": {"x": x, "y": 0.0, "z": 0.0},
    }
    source = ak.Array(
        [
            {"primaries": [particle("gamma", -1.0), particle("e-", 1.0)]},
            {"primaries": [particle("gamma", 0.0)]},
        ]
    )
    with Application(gdml=basic_gdml) as app:
        events = app.run(source)
    assert ak.to_list(ak.num(events.primaries)) == [2, 1]
    assert ak.to_list(events.primaries.particle) == [["gamma", "e-"], ["gamma"]]
