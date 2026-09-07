"""02 - GPS and configurable particle sources.

Shows particle gun vs General Particle Source (GPS), plus advanced GPS
commands and awkward-array primaries.
Run: python 02_gps_sources.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import awkward as ak
    import numpy as np

    import geant4_python_application as g4

    with g4.Application(gdml=g4.basic_gdml, seed=12) as app:
        # Particle gun
        app.generator.use_gun()
        print(f"generator type: {app.generator.type}")
        app.command("/gun/particle gamma")
        app.command("/gun/energy 2 MeV")
        events = app.run(2)
        print(f"gun primaries (keV): {ak.flatten(events.primaries.energy)}")

        # GPS with Python helpers
        app.generator.use_gps().particle("gamma").energy(2, "MeV")
        app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
        print(f"generator type: {app.generator.type}")
        events = app.run(2)
        energies = ak.to_numpy(ak.flatten(events.primaries.energy))
        print(f"GPS primaries (keV, expect ~2000): {energies}")
        assert np.allclose(energies, 2000)

        # Advanced GPS distribution via raw commands
        app.generator.commands(["/gps/pos/type Point", "/gps/pos/centre 0 0 0 cm"])
        events = app.run(1)
        print(f"advanced GPS: ran {len(events)} event(s)")

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, seed=12) as app:
            app.generator.use_gps().particle("gamma").energy(2, "MeV")
            app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
