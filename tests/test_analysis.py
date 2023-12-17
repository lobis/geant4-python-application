from __future__ import annotations

import platform

import awkward as ak
import numpy as np
import pytest
import requests

from geant4_python_application import Application

complexGdml = requests.get(
    "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"
).text


def test_events():
    with Application() as app:
        app.seed = 1000
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
    with Application() as app:
        app.seed = 1000
        app.setup_detector(gdml=complexGdml).setup_action()

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
        total = 2
        while (n := np.sum([len(_events) for _events in events])) < total:
            run_events = app.run(20)
            run_events = run_events[run_events.energy_in_volume(volume) > 0]
            events.append(run_events)
        events = ak.concatenate(events)
        # ak.to_parquet(events.hits(volume), "hits.parquet")
        hits = events.hits(volume)
        electrons = ak.concatenate([hit.electrons() for hit in hits])


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Not working on Windows. Why?"
)
@pytest.mark.parametrize("n_threads", [0, 8])
def test_photoelectric(n_threads):
    with Application(gdml=complexGdml, seed=1234, n_threads=n_threads) as app:
        sensitive_volume = "gasVolume"

        app.initialize()

        app.command("/gun/particle gamma")
        app.command("/gun/energy 10 keV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 20 cm")

        volumes = app.detector.physical_volumes_from_logical(sensitive_volume)
        assert len(volumes) == 1
        volume = list(volumes)[0]
        print("volume: ", volume)

        events = app.run(10000)
        sensitive_energy = events.energy_in_volume(volume)
        sensitive_energy_average = np.average(sensitive_energy)
        sensitive_energy_std = np.std(sensitive_energy)

        # unique_processes = np.unique(list(ak.flatten(ak.flatten(events.track.step.process))))
        assert np.isclose(sensitive_energy_average, 3.4841179413743117, rtol=5e-2)
        assert np.isclose(sensitive_energy_std, 4.706285949796168, rtol=5e-2)


@pytest.mark.skip(reason="seed produces different results on different machines")
def test_neutrons():
    with Application(gdml=complexGdml, seed=1234, n_threads=0) as app:
        sensitive_volume = "gasVolume"

        app.initialize()

        app.command("/gun/particle neutron")
        app.command("/gun/energy 100 keV")
        app.command("/gun/direction 0 0 -1")
        app.command("/gun/position 0 0 20 cm")

        volumes = app.detector.physical_volumes_from_logical(sensitive_volume)
        assert len(volumes) == 1
        volume = list(volumes)[0]
        print("volume: ", volume)

        events = app.run(10000)
        sensitive_energy = events.energy_in_volume(volume)
        assert np.isclose(np.max(sensitive_energy), 82.1415235313907, rtol=1e-3)

        events = events[sensitive_energy > 0]
        assert len(events) == 15


def test_muons():
    with Application(gdml=complexGdml, seed=1234, n_threads=0) as app:
        sensitive_volume = "gasVolume"

        app.initialize()

        app.command("/gun/particle mu-")
        app.command("/gun/energy 1 GeV")
        app.command("/gun/direction 0 -1 0")
        app.command("/gun/position 0 2 0 m")

        volumes = app.detector.physical_volumes_from_logical(sensitive_volume)
        assert len(volumes) == 1
        volume = list(volumes)[0]
        print("volume: ", volume)

        events = app.run(2000)
        sensitive_energy = events.energy_in_volume(volume)
        events = events[sensitive_energy > 0]

        sensitive_energy = events.energy_in_volume(volume)
        assert np.isclose(np.average(sensitive_energy), 24.821580016670598, rtol=1e-1)
        assert np.isclose(np.std(sensitive_energy), 16.09166011697945, rtol=1e-1)
