"""Python adaptation of Geant4 basic/B2: fixed target and tracker chambers."""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


def geometry() -> str:
    chambers = []
    for index in range(6):
        z = -50 + index * 35
        radius = 20 + index * 5
        chambers.append(
            f'<tube name="ChamberSolid{index}" rmin="0" rmax="{radius}" z="1" '
            'startphi="0" deltaphi="360" aunit="deg" lunit="mm"/>'
        )
    volumes = "".join(
        f'<volume name="ChamberLV{i}"><materialref ref="G4_Ar"/>'
        f'<solidref ref="ChamberSolid{i}"/></volume>' for i in range(6)
    )
    placements = "".join(
        f'<physvol name="Chamber{i}"><volumeref ref="ChamberLV{i}"/>'
        f'<position unit="mm" x="0" y="0" z="{-50 + i * 35}"/></physvol>'
        for i in range(6)
    )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<gdml><solids>
<box name="WorldSolid" x="300" y="300" z="500" lunit="mm"/>
<tube name="TargetSolid" rmin="0" rmax="25" z="10" startphi="0" deltaphi="360" aunit="deg" lunit="mm"/>
{''.join(chambers)}</solids><structure>
<volume name="TargetLV"><materialref ref="G4_Pb"/><solidref ref="TargetSolid"/></volume>
{volumes}<volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldSolid"/>
<physvol name="Target"><volumeref ref="TargetLV"/><position unit="mm" x="0" y="0" z="-90"/></physvol>
{placements}</volume></structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=100)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    with g4.Application(gdml=geometry(), physics="FTFP_BERT", seed=137) as app:
        app.set_event_fields({"id", "track_id", "step_energy", "step_volume", "step_position"})
        app.detector.magnetic_field = (0.2, 0.0, 0.0)
        app.commands(["/gun/particle proton", "/gun/energy 3 GeV", "/gun/position 0 0 -20 cm", "/gun/direction 0 0 1"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    steps = ak.flatten(events.track.step, axis=-1)
    tracker_hits = steps[
        (steps.energy > 0) & ak.str.starts_with(steps.volume, "Chamber")
    ]
    print(f"events: {len(events)}, tracker hits: {len(ak.flatten(tracker_hits.energy, axis=None))}")


if __name__ == "__main__":
    main()
