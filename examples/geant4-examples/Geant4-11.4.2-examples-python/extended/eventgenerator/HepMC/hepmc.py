"""Python adapter for extended/eventgenerator/HepMC.

Reads a small HepMC2 ASCII subset through the package's Python adapter and
transports final-state particles.  It does not embed a native HepMC library.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geant4_python_application as g4

SAMPLE = """E 0 1 1
P 1 22 0 0 1 1 0 1
P 2 11 0.1 0 0.5 0.6 0.000511 1
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("-n", "--events", type=int, default=1, help="accepted for the common audit interface")
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    text = args.input.read_text() if args.input else SAMPLE
    primaries = g4.io.hepmc_to_primaries(text)

    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=137) as app:
        if not args.batch:
            app.visualize()
            return
        events = app.run(primaries)
    print(f"parsed and transported {len(events)} HepMC particles")
    assert len(events) == len(primaries)


if __name__ == "__main__":
    main()
