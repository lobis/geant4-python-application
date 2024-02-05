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
@pytest.mark.skip(reason="This test is not working atm")
def test_awkward_primaries(n_threads):
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
