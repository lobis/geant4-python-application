"""Python optical-transport adaptation of extended/optical/wls.

The detector is a polystyrene-like WLS core inside lower-index cladding.  A
violet optical photon is absorbed and can be re-emitted at lower energy by the
native Geant4 wavelength-shifting process.
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

    with g4.Application(gdml=g4.optical.wls_fiber_gdml, optical=True, seed=521) as app:
        app.commands(
            [
                "/gun/particle opticalphoton",
                "/gun/energy 3.5 eV",
                "/gun/position 0 0 -190 mm",
                "/gun/direction 0 0 1",
                "/gun/polarization 1 0 0",
            ]
        )
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)

    particles = ak.flatten(events.track.particle, axis=None)
    photons = int(ak.sum(particles == "opticalphoton"))
    print(f"events: {len(events)}, WLS optical-photon tracks: {photons}")
    assert photons >= args.events


if __name__ == "__main__":
    main()
