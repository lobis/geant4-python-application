"""Python adaptation of extended/eventgenerator/exgps."""

from __future__ import annotations

import argparse
from pathlib import Path

import awkward as ak
import geant4_python_application as g4
import numpy as np

GDML = '''<gdml><solids><box name="WorldS" x="1000" y="1000" z="1000" lunit="mm"/><box name="AlS" x="200" y="200" z="200" lunit="mm"/><orb name="SiS" r="50" lunit="mm"/></solids><structure><volume name="SiLV"><materialref ref="G4_SILICON_DIOXIDE"/><solidref ref="SiS"/></volume><volume name="AlLV"><materialref ref="G4_Al"/><solidref ref="AlS"/><physvol name="Silica"><volumeref ref="SiLV"/></physvol></volume><volume name="World"><materialref ref="G4_Galactic"/><solidref ref="WorldS"/><physvol name="Aluminium"><volumeref ref="AlLV"/></physvol></volume></structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--events", type=int, default=1000)
    p.add_argument("--batch", action="store_true")
    p.add_argument("-o", "--output", type=Path, default=Path("exgps_primaries.npz"))
    args = p.parse_args()
    with g4.Application(gdml=GDML, seed=137) as app:
        app.generator.use_gps().particle("gamma")
        app.generator.commands([
            "/gps/pos/type Volume", "/gps/pos/shape Sphere", "/gps/pos/radius 4 cm",
            "/gps/ang/type iso", "/gps/ene/type Lin", "/gps/ene/min 100 keV", "/gps/ene/max 2 MeV",
        ])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    energy = ak.to_numpy(ak.flatten(events.primaries.energy))
    np.savez(args.output, energy_keV=energy)
    print(f"events: {len(events)}, energy range: {energy.min():.2f}-{energy.max():.2f} keV; wrote {args.output}")


if __name__ == "__main__":
    main()
