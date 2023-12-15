from __future__ import annotations

import awkward as ak
import numpy as np
import requests

from geant4_python_application import Application

complexGdml = requests.get(
    "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"
).text


def test_events():
    with Application() as app:
        app.seed = 1000
        app.setup_manager(4).setup_physics().setup_detector(
            gdml=complexGdml
        ).setup_action()

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
        while (n := np.sum([len(energy) for energy in energy_arrays])) < 1e4:
            events = app.run(1000)
            energy = events.energy_in_volume(volume)
            energy_arrays.append(energy[energy > 0])
            # discard 0 energy events
        energies = np.concatenate(energy_arrays)


def test_sensitive():
    with Application() as app:
        app.seed = 1000
        app.setup_manager(4).setup_physics().setup_detector(
            gdml=complexGdml
        ).setup_action()

        sensitive_volume = "gasVolume"
        app.detector.sensitive_volumes = {sensitive_volume}

        app.initialize()

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 MeV")
        app.command("/gun/direction 0 -1 0")
        app.command("/gun/position 0 10 0 m")

        volumes = app.detector.physical_volumes_from_logical(sensitive_volume)
        assert len(volumes) == 1
        volume = list(volumes)[0]
        print("volume: ", volume)
        events = []
        total = 5
        while (n := np.sum([len(_events) for _events in events])) < total:
            run_events = app.run(50)
            run_events = run_events[run_events.energy_in_volume(volume) > 0]
            events.append(run_events)
        events = ak.concatenate(events)
        ak.to_parquet(events.hits(volume), "hits.parquet")
        hits = events.hits(volume)
        electrons = ak.concatenate([hit.electrons() for hit in hits])
