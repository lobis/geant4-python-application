"""Python/GDML adaptation of extended/parameterisations/Par01.

The repeated detector cells are expanded into fixed GDML placements before
initialization.  This covers static parameterised layouts without exposing a
live G4VPVParameterisation callback.
"""

from __future__ import annotations

import argparse

import geant4_python_application as g4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=10)
    parser.add_argument("--cells", type=int, default=12)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    gdml = g4.geometry.linear_array_gdml(args.cells, spacing_mm=15, box_size_mm=5)

    with g4.Application(gdml=gdml, seed=137) as app:
        app.commands(["/gun/particle geantino", "/gun/position -120 0 0 mm", "/gun/direction 1 0 0"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    print(f"events: {len(events)}, expanded detector cells: {args.cells}")


if __name__ == "__main__":
    main()
