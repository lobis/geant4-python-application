"""04 - Uniform magnetic and electric fields.

Shows setting a uniform global B field (tesla) and E field (kV/cm).
E uses G4EqMagElectricField + ClassicalRK4; B-only uses G4GlobalMagFieldMessenger.
Run: python 04_magnetic_electric_fields.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import geant4_python_application as g4

    with g4.Application(gdml=g4.basic_gdml, seed=14) as app:
        app.detector.magnetic_field = (0.0, 0.0, 1.0)  # tesla
        app.detector.electric_field = (0.0, 0.0, 0.5)  # kV/cm
        print(f"B = {app.detector.magnetic_field} T")
        print(f"E = {app.detector.electric_field} kV/cm")
        app.command("/gun/particle e-")
        app.command("/gun/energy 5 MeV")
        events = app.run(2)
        print(f"ran {len(events)} events with combined B+E field")

    # B-only (original path)
    with g4.Application(gdml=g4.basic_gdml, seed=14) as app:
        app.detector.magnetic_field = (0.0, 0.0, 1.5)
        print(f"B-only = {app.detector.magnetic_field} T")
        events = app.run(1)
        print(f"ran {len(events)} event with B-only field")

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, seed=14) as app:
            app.detector.magnetic_field = (0.0, 0.0, 1.0)
            app.detector.electric_field = (0.0, 0.0, 0.5)
            app.command("/gun/particle e-")
            app.command("/gun/energy 5 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
