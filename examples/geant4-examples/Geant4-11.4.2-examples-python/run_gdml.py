"""Run a GDML detector with geant4-python-application and the Qt viewer."""

from __future__ import annotations

import argparse
from pathlib import Path

import geant4_python_application as g4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gdml", type=Path, help="path to a GDML geometry file")
    parser.add_argument("-n", "--events", type=int, default=100)
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--command", action="append", default=[], help="Geant4 command")
    args = parser.parse_args()

    geometry = args.gdml.read_text()
    commands = args.command or [
        "/gun/particle geantino",
        "/gun/energy 1 GeV",
        "/gun/direction 0 0 1",
    ]
    with g4.Application(gdml=geometry, seed=137) as app:
        app.commands(commands)
        if args.batch:
            print(f"events simulated: {len(app.run(args.events))}")
        else:
            app.visualize([
                "/vis/open OGL", "/vis/drawVolume",
                "/vis/viewer/set/style wireframe",
                "/vis/scene/add/trajectories smooth",
                "/tracking/storeTrajectory 1",
                "/vis/scene/endOfEventAction accumulate 100",
            ])


if __name__ == "__main__":
    main()
