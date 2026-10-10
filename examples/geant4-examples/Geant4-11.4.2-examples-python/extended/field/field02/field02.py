"""Python adaptation of extended/field/field02 constant-electric-field test."""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4

GDML = '''<gdml><solids><box name="WorldS" x="300" y="300" z="500" lunit="mm"/><box name="AbsS" x="200" y="200" z="300" lunit="mm"/></solids><structure><volume name="AbsLV"><materialref ref="G4_Al"/><solidref ref="AbsS"/></volume><volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldS"/><physvol name="Absorber"><volumeref ref="AbsLV"/></physvol></volume></structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--events", type=int, default=100)
    p.add_argument("--field", type=float, default=0.5, help="electric field in kV/cm")
    p.add_argument("--batch", action="store_true")
    args = p.parse_args()
    with g4.Application(gdml=GDML, physics="FTFP_BERT", seed=137) as app:
        app.detector.electric_field = (args.field, 0.0, 0.0)
        app.set_event_fields({"id", "track_id", "step_energy", "step_volume", "step_position"})
        app.commands(["/gun/particle e-", "/gun/energy 10 MeV", "/gun/position 0 0 -20 cm", "/gun/direction 0 0 1"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    steps = events.track.step
    edep = float(ak.sum(steps.energy[steps.volume == "Absorber"]))
    print(f"events: {len(events)}, E=({args.field},0,0) kV/cm, absorber energy: {edep:.3f} keV")


if __name__ == "__main__":
    main()
