"""08 - DNA chemistry and medical extensions.

Shows adding Geant4-DNA physics (e.g. option2) for low-energy electron
transport in water. Chemistry constructors are listed but only the
physical stage is run here.
Run: python 08_dna_medical.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import geant4_python_application as g4

    dna = [x for x in g4.Application.available_extra_physics() if "DNA" in x]
    print(f"DNA constructors: {dna}")

    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=19) as app:
        app.add_physics("G4EmDNAPhysics_option2")
        app.command("/gun/particle e-")
        app.command("/gun/energy 100 keV")
        events = app.run(1)
        print(f"ran {len(events)} event with G4EmDNAPhysics_option2")

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=19) as app:
            app.add_physics("G4EmDNAPhysics_option2")
            app.command("/gun/particle e-")
            app.command("/gun/energy 100 keV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
