"""Python adaptation of extended/eventgenerator/particleGun sampling modes."""

from __future__ import annotations

import argparse
import math

import awkward as ak
import geant4_python_application as g4
import numpy as np


def _particle(position, direction, energy=1000.0):
    return {"particle": "geantino", "energy": energy, "position": dict(zip("xyz", position)), "direction": dict(zip("xyz", direction))}


def primaries(count: int, mode: int, seed: int) -> ak.Array:
    rng = np.random.default_rng(seed)
    records = []
    for _ in range(count):
        phi = rng.uniform(0, 2 * math.pi)
        if mode == 1:
            position = (50 * math.cos(phi), 50 * math.sin(phi), rng.uniform(-50, 50))
            radial = (math.cos(phi), math.sin(phi), 0.0)
            records.append({"primaries": [
                _particle(position, radial),
                _particle(tuple(-x for x in position), tuple(-x for x in radial)),
                _particle((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
            ]})
            continue
        if mode == 2:
            energy = float(rng.choice([100, 250, 500, 1000], p=[0.1, 0.3, 0.4, 0.2]))
            position = (0.0, 0.0, 0.0)
            direction = (0.0, 0.0, 1.0)
        elif mode == 4:
            radius = np.cbrt(rng.uniform(20**3, 80**3))
            costheta = rng.uniform(-1, 1)
            sintheta = math.sqrt(1 - costheta**2)
            position = (radius * sintheta * math.cos(phi), radius * sintheta * math.sin(phi), radius * costheta)
            direction = tuple(-value / radius for value in position)
            energy = 1000.0
        else:
            alpha = rng.uniform(0, math.radians(15 if mode == 3 else 30))
            direction = (math.sin(alpha) * math.cos(phi), math.sin(alpha) * math.sin(phi), math.cos(alpha))
            position, energy = (0.0, 0.0, -100.0), 1000.0
        records.append(_particle(position, direction, energy))
    return ak.Array(records)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--events", type=int, default=1000)
    p.add_argument("--mode", type=int, choices=(0, 1, 2, 3, 4), default=0)
    p.add_argument("--batch", action="store_true")
    args = p.parse_args()
    source = primaries(args.events, args.mode, 137)
    with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
        if not args.batch:
            app.visualize()
            return
        events = app.run(source)
    print(f"mode {args.mode}: generated and transported {len(events)} primaries")


if __name__ == "__main__":
    main()
