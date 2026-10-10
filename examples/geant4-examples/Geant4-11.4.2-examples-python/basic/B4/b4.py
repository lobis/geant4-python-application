"""Python port of Geant4 basic/B4: lead/liquid-argon sampling calorimeter."""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


def geometry() -> str:
    layers = []
    for index in range(10):
        z = -67.5 + index * 15
        layers.append(
            f'<physvol name="Absorber{index}"><volumeref ref="AbsorberLV"/>'
            f'<position unit="mm" x="0" y="0" z="{z - 2.5}"/></physvol>'
            f'<physvol name="Gap{index}"><volumeref ref="GapLV"/>'
            f'<position unit="mm" x="0" y="0" z="{z + 5}"/></physvol>'
        )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<gdml><solids>
  <box name="WorldSolid" x="120" y="120" z="180" lunit="mm"/>
  <box name="AbsorberSolid" x="100" y="100" z="10" lunit="mm"/>
  <box name="GapSolid" x="100" y="100" z="5" lunit="mm"/>
</solids><structure>
  <volume name="AbsorberLV"><materialref ref="G4_Pb"/><solidref ref="AbsorberSolid"/></volume>
  <volume name="GapLV"><materialref ref="G4_lAr"/><solidref ref="GapSolid"/></volume>
  <volume name="World"><materialref ref="G4_Galactic"/><solidref ref="WorldSolid"/>{''.join(layers)}</volume>
</structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=100)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()

    with g4.Application(gdml=geometry(), seed=137) as app:
        app.set_event_fields({"id", "track_id", "step_energy", "step_volume"})
        app.commands([
            "/gun/particle e-", "/gun/energy 1 GeV",
            "/gun/position 0 0 -10 cm", "/gun/direction 0 0 1",
        ])
        if not args.batch:
            app.visualize([
                "/vis/open OGL", "/vis/drawVolume", "/vis/viewer/set/style wireframe",
                "/vis/scene/add/trajectories smooth", "/tracking/storeTrajectory 1",
                "/vis/scene/endOfEventAction accumulate 100",
            ])
            return
        events = app.run(args.events)

    energy = events.track.step.energy
    volume = events.track.step.volume
    absorber = ak.sum(energy[ak.str.starts_with(volume, "Absorber")])
    gap = ak.sum(energy[ak.str.starts_with(volume, "Gap")])
    print(f"absorber deposited energy: {float(absorber):.3f} keV")
    print(f"gap deposited energy: {float(gap):.3f} keV")


if __name__ == "__main__":
    main()
