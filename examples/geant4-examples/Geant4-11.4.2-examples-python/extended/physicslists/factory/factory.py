"""Python adaptation of extended/physicslists/factory."""

from __future__ import annotations

import argparse

import geant4_python_application as g4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=10)
    parser.add_argument("--physics", default="FTFP_BERT")
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    available = g4.Application.available_physics_lists()
    if args.physics not in available:
        raise SystemExit(f"unknown physics list {args.physics!r}; choose from: {', '.join(available)}")

    with g4.Application(gdml=g4.basic_gdml, physics=args.physics, seed=137) as app:
        app.commands(["/gun/particle proton", "/gun/energy 1 GeV", "/gun/position 0 0 -400 mm", "/gun/direction 0 0 1"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    print(f"physics list: {args.physics}; events: {len(events)}; factory lists: {len(available)}")


if __name__ == "__main__":
    main()
