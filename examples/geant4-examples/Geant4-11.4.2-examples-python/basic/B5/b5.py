"""Python adaptation of Geant4 basic/B5: double-arm spectrometer."""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


def geometry() -> str:
    placements = []
    specs = [
        ("Hodoscope1", "HodoLV", -180), ("Chamber1", "ChamberLV", -130),
        ("FieldRegion", "FieldLV", 0), ("Hodoscope2", "HodoLV", 130),
        ("Chamber2", "ChamberLV", 170), ("ECal", "ECalLV", 220),
        ("HCal", "HCalLV", 290),
    ]
    for name, logical, z in specs:
        placements.append(f'<physvol name="{name}"><volumeref ref="{logical}"/><position unit="mm" x="0" y="0" z="{z}"/></physvol>')
    return f'''<?xml version="1.0" encoding="utf-8"?>
<gdml><solids><box name="WorldSolid" x="500" y="500" z="800" lunit="mm"/>
<box name="HodoSolid" x="150" y="8" z="8" lunit="mm"/><box name="ChamberSolid" x="180" y="120" z="10" lunit="mm"/>
<tube name="FieldSolid" rmin="0" rmax="80" z="100" startphi="0" deltaphi="360" aunit="deg" lunit="mm"/>
<box name="ECalSolid" x="180" y="180" z="60" lunit="mm"/><box name="HCalSolid" x="220" y="220" z="100" lunit="mm"/></solids><structure>
<volume name="HodoLV"><materialref ref="G4_PLASTIC_SC_VINYLTOLUENE"/><solidref ref="HodoSolid"/></volume>
<volume name="ChamberLV"><materialref ref="G4_Ar"/><solidref ref="ChamberSolid"/></volume>
<volume name="FieldLV"><materialref ref="G4_AIR"/><solidref ref="FieldSolid"/></volume>
<volume name="ECalLV"><materialref ref="G4_CESIUM_IODIDE"/><solidref ref="ECalSolid"/></volume>
<volume name="HCalLV"><materialref ref="G4_Pb"/><solidref ref="HCalSolid"/></volume>
<volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldSolid"/>{''.join(placements)}</volume>
</structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=100)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    with g4.Application(gdml=geometry(), physics="FTFP_BERT", seed=137) as app:
        app.detector.magnetic_field = (0.0, 1.0, 0.0)
        app.set_event_fields({"id", "track_id", "step_energy", "step_time", "step_volume", "step_position"})
        app.commands(["/gun/particle proton", "/gun/energy 1 GeV", "/gun/position 0 0 -35 cm", "/gun/direction 0 0 1"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    for volume in ("Hodoscope", "Chamber", "ECal", "HCal"):
        mask = ak.str.starts_with(events.track.step.volume, volume)
        print(f"{volume} energy: {float(ak.sum(events.track.step.energy[mask])):.3f} keV")


if __name__ == "__main__":
    main()
