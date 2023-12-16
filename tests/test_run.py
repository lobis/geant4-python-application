from __future__ import annotations

import awkward as ak
import pytest
import requests

from geant4_python_application import Application, basic_gdml

complex_gdml = requests.get(
    "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"
).text


@pytest.mark.parametrize("n_threads", [0, 4])
def test_awkward_primaries(n_threads):
    primaries = ak.Array(
        [
            {
                "particle": "neutron",
                "energy": 100,
                "direction": {"x": 0, "y": -1, "z": 0},
                "position": {"x": 0, "y": 10, "z": 0},
            },
        ]
        * 100
    )
    with Application(gdml=basic_gdml, n_threads=n_threads) as app:
        events = app.run(primaries)
        assert len(events) == len(primaries)
