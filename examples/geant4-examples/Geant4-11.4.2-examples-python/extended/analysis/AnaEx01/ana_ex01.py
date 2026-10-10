"""Python adaptation of extended/analysis/AnaEx01 sampling-calorimeter analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import awkward as ak
import geant4_python_application as g4
import numpy as np

from importlib.util import module_from_spec, spec_from_file_location


def load_b4_geometry():
    path = Path(__file__).parents[3] / "basic" / "B4" / "b4.py"
    spec = spec_from_file_location("g4_b4_geometry", path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.geometry()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--events", type=int, default=100)
    p.add_argument("--batch", action="store_true")
    p.add_argument("-o", "--output", type=Path, default=Path("ana_ex01.csv"))
    args = p.parse_args()
    with g4.Application(gdml=load_b4_geometry(), physics="FTFP_BERT", seed=137) as app:
        app.set_event_fields({"id", "track_id", "step_energy", "step_volume"})
        app.commands(["/gun/particle e-", "/gun/energy 1 GeV", "/gun/position 0 0 -10 cm", "/gun/direction 0 0 1"])
        if not args.batch:
            app.visualize()
            return
        events = app.run(args.events)
    step = events.track.step
    absorber = ak.to_numpy(ak.sum(ak.flatten(step.energy[ak.str.starts_with(step.volume, "Absorber")], axis=-1), axis=1))
    gap = ak.to_numpy(ak.sum(ak.flatten(step.energy[ak.str.starts_with(step.volume, "Gap")], axis=-1), axis=1))
    np.savetxt(args.output, np.column_stack((np.arange(len(events)), absorber, gap)), delimiter=",", header="event,EAbs_keV,EGap_keV", comments="")
    print(f"events: {len(events)}, wrote {args.output}; mean EAbs={absorber.mean():.3f} keV, EGap={gap.mean():.3f} keV")


if __name__ == "__main__":
    main()
