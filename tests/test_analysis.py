from __future__ import annotations

import awkward as ak
import numpy as np
import requests

from geant4_python_application import Application

complexGdml = requests.get(
    "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"
).text


def test_events():
    with Application(seed=1000) as app:
        app.setup_detector(gdml=complexGdml)

        sensitive_volume = "gasVolume"
        app.detector.sensitive_volumes = {sensitive_volume}

        app.initialize()

        app.set_event_fields({"id", "step_energy", "step_volume"})

        app.command("/gun/particle gamma")
        app.command("/gun/energy 8 keV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 10 cm")

        volumes = app.detector.physical_volumes_from_logical(sensitive_volume)
        assert len(volumes) == 1
        volume = list(volumes)[0]

        energy_arrays = []
        while (n := np.sum([len(energy) for energy in energy_arrays])) < 5e3:
            events = app.run(1000)
            energy = events.energy_in_volume(volume)
            energy_arrays.append(energy[energy > 0])
            # discard 0 energy events
        energies = np.concatenate(energy_arrays)


def test_sensitive():
    with Application(gdml=complexGdml, seed=1234) as app:
        volume_logical = "gasVolume"

        app.initialize()

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 -1 0")
        app.command("/gun/position 0 10 0 m")

        volumes = app.detector.physical_volumes_from_logical(volume_logical)
        assert len(volumes) == 1
        volume = list(volumes)[0]
        print("volume: ", volume)
        events = app.run(1000)
        energy_in_sensitive = events.energy_in_volume(volume)
        for i, energy in enumerate(
            ak.flatten(ak.sum(events.track.step.energy, axis=-1))
        ):
            print(f"event {i} energy: {energy}")

        events = events[energy_in_sensitive > 0]
        print("n: ", len(events))
        return

        assert app.seed == 1234
        assert len(events) == 5
        hits = events.hits(volume)
        np.isclose(hits.energy[0][0:5], [0.0401, 0.00271, 0.00391, 0.389, 0.204])
        electrons = ak.concatenate([hit.electrons() for hit in hits])
