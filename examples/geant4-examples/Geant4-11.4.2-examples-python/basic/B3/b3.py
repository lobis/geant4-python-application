"""Python adaptation of Geant4 basic/B3: schematic PET scanner."""

from __future__ import annotations

import argparse
import math

import awkward as ak
import geant4_python_application as g4


def geometry() -> str:
    placements = []
    for ring in range(3):
        z = (ring - 1) * 25
        for crystal in range(24):
            angle = crystal * 15
            radians = math.radians(angle)
            x, y = 100 * math.cos(radians), 100 * math.sin(radians)
            placements.append(
                f'<physvol name="Crystal_{ring}_{crystal}"><volumeref ref="CrystalLV"/>'
                f'<position unit="mm" x="{x:.6f}" y="{y:.6f}" z="{z}"/>'
                f'<rotation unit="deg" x="0" y="0" z="{angle}"/></physvol>'
            )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<gdml><solids><box name="WorldSolid" x="300" y="300" z="250" lunit="mm"/>
<tube name="PatientSolid" rmin="0" rmax="50" z="100" startphi="0" deltaphi="360" aunit="deg" lunit="mm"/>
<box name="CrystalSolid" x="8" y="20" z="20" lunit="mm"/></solids><structure>
<volume name="PatientLV"><materialref ref="G4_BRAIN_ICRP"/><solidref ref="PatientSolid"/></volume>
<volume name="CrystalLV"><materialref ref="G4_SODIUM_IODIDE"/><solidref ref="CrystalSolid"/></volume>
<volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldSolid"/>
<physvol name="Patient"><volumeref ref="PatientLV"/></physvol>{''.join(placements)}</volume>
</structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=100)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    with g4.Application(gdml=geometry(), physics="FTFP_BERT", seed=137) as app:
        app.add_physics("G4RadioactiveDecayPhysics")
        app.set_event_fields({"id", "track_id", "step_energy", "step_volume"})
        app.commands(["/gun/particle gamma", "/gun/energy 511 keV", "/gun/position 0 0 0 mm", "/gun/direction 1 0 0"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    crystal = ak.sum(events.track.step.energy[ak.str.starts_with(events.track.step.volume, "Crystal")])
    patient = ak.sum(events.track.step.energy[events.track.step.volume == "Patient"])
    print(f"events: {len(events)}, crystal energy: {float(crystal):.3f} keV, patient energy: {float(patient):.3f} keV")


if __name__ == "__main__":
    main()
