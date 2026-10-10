"""Python port of Geant4 basic/B1: tissue-and-bone phantom."""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


GDML = R'''<?xml version="1.0" encoding="utf-8"?>
<gdml>
  <solids>
    <box name="WorldSolid" x="240" y="240" z="360" lunit="mm"/>
    <box name="EnvelopeSolid" x="200" y="200" z="300" lunit="mm"/>
    <cone name="TissueSolid" rmin1="0" rmax1="20" rmin2="0" rmax2="40" z="60" startphi="0" deltaphi="360" aunit="deg" lunit="mm"/>
    <trd name="BoneSolid" x1="120" x2="120" y1="100" y2="160" z="60" lunit="mm"/>
  </solids>
  <structure>
    <volume name="TissueLV"><materialref ref="G4_A-150_TISSUE"/><solidref ref="TissueSolid"/></volume>
    <volume name="BoneLV"><materialref ref="G4_BONE_COMPACT_ICRU"/><solidref ref="BoneSolid"/></volume>
    <volume name="EnvelopeLV">
      <materialref ref="G4_WATER"/><solidref ref="EnvelopeSolid"/>
      <physvol name="Tissue"><volumeref ref="TissueLV"/><position unit="mm" x="0" y="20" z="-70"/></physvol>
      <physvol name="Bone"><volumeref ref="BoneLV"/><position unit="mm" x="0" y="-10" z="70"/></physvol>
    </volume>
    <volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldSolid"/>
      <physvol name="Envelope"><volumeref ref="EnvelopeLV"/></physvol>
    </volume>
  </structure>
  <setup name="Default" version="1.0"><world ref="World"/></setup>
</gdml>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=100)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()

    with g4.Application(gdml=GDML, seed=137) as app:
        app.set_event_fields({"id", "track_id", "step_energy", "step_volume"})
        app.commands([
            "/gun/particle e-", "/gun/energy 10 MeV",
            "/gun/position 0 0 -20 cm", "/gun/direction 0 0 1",
        ])
        if not args.batch:
            app.visualize([
                "/vis/open OGL", "/vis/drawVolume", "/vis/viewer/set/style wireframe",
                "/vis/scene/add/trajectories smooth", "/tracking/storeTrajectory 1",
                "/vis/scene/endOfEventAction accumulate 100",
            ])
            return
        events = app.run(args.events)

    for volume in ("Tissue", "Bone"):
        deposited = ak.sum(events.track.step.energy[events.track.step.volume == volume])
        print(f"{volume} deposited energy: {float(deposited):.3f} keV")


if __name__ == "__main__":
    main()
