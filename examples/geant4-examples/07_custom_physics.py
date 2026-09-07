"""07 - Custom physics processes.

Shows registering extra G4VPhysicsConstructors by name on top of a
reference or custom list, before initialize/run.
Run: python 07_custom_physics.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import geant4_python_application as g4

    print(f"extra physics: {g4.Application.available_extra_physics()}")

    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=17) as app:
        app.add_physics("G4EmExtraPhysics")
        app.command("/gun/particle gamma")
        app.command("/gun/energy 1 MeV")
        events = app.run(1)
        print(f"ran {len(events)} event with G4EmExtraPhysics added")

    # Unknown constructor raises a clear error
    try:
        with g4.Application(gdml=g4.basic_gdml, seed=17) as app:
            app.add_physics("NOT_A_PHYSICS")
    except Exception as exc:
        print(f"unknown constructor correctly raised: {exc}")

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=17) as app:
            app.add_physics("G4EmExtraPhysics")
            app.command("/gun/particle gamma")
            app.command("/gun/energy 1 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
