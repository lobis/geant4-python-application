"""03 - Scoring meshes and hit collections.

Shows offline scoring over recorded steps: per-event energy deposit,
Cartesian energy mesh (numpy histogramdd), and hit filtering.
Run: python 03_scoring_meshes_hits.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import awkward as ak

    import geant4_python_application as g4

    with g4.Application(gdml=g4.basic_gdml, seed=13) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 10 MeV")
        events = app.run(3)

    print(f"event fields: {events.fields}")

    edep = g4.Scoring.energy_deposit(events)
    print(f"deposited energy per event (keV): {ak.to_numpy(edep)}")

    mesh, edges = g4.Scoring.energy_mesh(events, bins=(4, 5, 6))
    print(f"mesh shape: {mesh.shape}, total: {mesh.sum():.2f} keV")

    hits = events.hits()
    n_hits = len(ak.flatten(hits.energy, axis=None))
    print(f"total positive-energy steps (hits): {n_hits}")

    # Volume-restricted scoring (physical volume name 'box' in basic_gdml)
    edep_box = g4.Scoring.energy_deposit(events, volume="box")
    print(f"energy in 'box' per event (keV): {ak.to_numpy(edep_box)}")

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, seed=13) as app:
            app.command("/gun/particle e-")
            app.command("/gun/energy 10 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
