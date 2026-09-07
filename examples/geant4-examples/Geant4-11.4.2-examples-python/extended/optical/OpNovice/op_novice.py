"""Python adaptation of extended/optical/OpNovice."""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--events", type=int, default=10)
    p.add_argument("--batch", action="store_true")
    args = p.parse_args()
    with g4.Application(gdml=g4.optical.optical_water_gdml, optical=True, seed=137) as app:
        app.commands(g4.optical.scintillation_commands(max_cerenkov=100))
        app.commands(["/gun/particle e-", "/gun/energy 10 MeV", "/gun/position 0 0 0 mm", "/gun/direction 1 0 0"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    particles = ak.flatten(events.track.particle, axis=None)
    optical = int(ak.sum(particles == "opticalphoton"))
    print(f"events: {len(events)}, optical photons tracked: {optical}")
    assert optical > 0


if __name__ == "__main__":
    main()
