"""Python optical-transport adaptation of extended/optical/LXe.

This covers liquid-xenon scintillation and optical boundary transport.  The
official example's custom PMT hit collection is represented by track analysis
after the run because Python sensitive-detector callbacks are not yet bound.
"""

from __future__ import annotations

import argparse

import awkward as ak
import geant4_python_application as g4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=10)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()

    with g4.Application(gdml=g4.optical.lxe_scintillator_gdml, optical=True, seed=137) as app:
        app.commands(g4.optical.scintillation_commands(max_cerenkov=100))
        app.commands(
            [
                "/gun/particle e-",
                "/gun/energy 1 MeV",
                "/gun/position 0 0 0 mm",
                "/gun/direction 1 0 0",
            ]
        )
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)

    particles = ak.flatten(events.track.particle, axis=None)
    photons = int(ak.sum(particles == "opticalphoton"))
    print(f"events: {len(events)}, liquid-xenon optical photons tracked: {photons}")
    assert photons > 0


if __name__ == "__main__":
    main()
