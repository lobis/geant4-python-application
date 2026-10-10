"""Multi-primary Python adaptation of extended/runAndEvent/RE01.

Each Geant4 event contains two independent primary vertices.  This exercises
the package's native nested-primary event support and preserves both vertices
in the returned Awkward event record.
"""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


def primary(particle: str, x: float) -> dict:
    return {
        "particle": particle,
        "energy": 1000.0,
        "position": {"x": x, "y": 0.0, "z": -300.0},
        "direction": {"x": 0.0, "y": 0.0, "z": 1.0},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=10)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    source = ak.Array(
        [{"primaries": [primary("gamma", -10.0), primary("e-", 10.0)]} for _ in range(args.events)]
    )

    with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
        if not args.batch:
            app.visualize()
            return
        events = app.run(source)
    counts = ak.to_list(ak.num(events.primaries))
    print(f"events: {len(events)}, primary vertices: {sum(counts)}")
    assert counts == [2] * args.events


if __name__ == "__main__":
    main()
