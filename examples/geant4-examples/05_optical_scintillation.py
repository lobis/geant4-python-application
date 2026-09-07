"""05 - Optical materials, surfaces and scintillation.

Uses GDML-defined RINDEX/ABSLENGTH/SCINTILLATION + skinsurface (see
Geant4 OpNovice) with G4OpticalPhysics. Verifies opticalphoton production.
Run: python 05_optical_scintillation.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import awkward as ak

    import geant4_python_application as g4
    from geant4_python_application import optical as gopt

    print(f"tuning commands: {gopt.scintillation_commands()}")

    with g4.Application(gdml=gopt.optical_water_gdml, optical=True, seed=15) as app:
        app.commands(gopt.scintillation_commands(stack_photons=True, max_cerenkov=100))
        app.command("/gun/particle e-")
        app.command("/gun/energy 10 MeV")
        app.command("/gun/position 0 0 0 mm")
        app.command("/gun/direction 1 0 0")
        events = app.run(2)
        print(f"ran {len(events)} events with optical physics")
        parts = sorted(set(ak.to_list(ak.flatten(events.track.particle, axis=None))))
        print(f"track particles: {parts}")
        assert "opticalphoton" in parts, "expected scintillation/Cerenkov photons"

    if "--vis" in sys.argv:
        with g4.Application(gdml=gopt.optical_water_gdml, optical=True, seed=15) as app:
            app.command("/gun/particle e-")
            app.command("/gun/energy 10 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
