"""Rutherford gold foil experiment, ported from the C++ example to geant4-python-application.

5.5 MeV alphas fired at a 500 nm gold foil in vacuum; records the scattering
angle and exit energy of each primary alpha as it leaves the foil.
"""

from __future__ import annotations

import argparse
import csv

import awkward as ak
import numpy as np

import geant4_python_application as g4
from geant4_python_application.application import Message

# World and foil match DetectorConstruction.cc. G4Box takes half-lengths and
# GDML takes full lengths, so every value here is twice the C++ one.
GOLD_FOIL_GDML = R"""<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">

    <solids>
        <box name="WorldSolid" x="200" y="200" z="300" lunit="mm"/>
        <box name="GoldFoilSolid" x="10" y="10" z="0.0005" lunit="mm"/>
    </solids>

    <structure>
        <volume name="GoldFoilLogical">
            <materialref ref="G4_Au"/>
            <solidref ref="GoldFoilSolid"/>
        </volume>

        <volume name="World">
            <materialref ref="G4_Galactic"/>
            <solidref ref="WorldSolid"/>

            <physvol name="GoldFoilPhysical">
                <volumeref ref="GoldFoilLogical"/>
                <position name="foilPosition" unit="mm" x="0" y="0" z="0"/>
            </physvol>
        </volume>
    </structure>

    <setup name="Default" version="1.0">
        <world ref="World"/>
    </setup>
</gdml>
"""

FOIL = "GoldFoilPhysical"


def scattering(events: ak.Array) -> tuple[np.ndarray, np.ndarray]:
    """Angle (deg) and exit energy (MeV) of each primary alpha leaving the foil.

    Mirrors SteppingAction.cc: primary track only, on the step whose pre-volume
    is the foil and whose post-volume is not.
    """
    tracks = events.track
    steps = tracks.step[(tracks.id == 1) & (tracks.particle == "alpha")]
    exiting = (steps.volume == FOIL) & (steps.volume_post != FOIL)

    # momentum is a unit vector, so the polar angle from the +z beam axis is acos(z)
    momentum_z = ak.flatten(steps.momentum[exiting].pz, axis=None)
    energy_kev = ak.flatten(steps.track_kinetic_energy[exiting], axis=None)

    angle = np.degrees(np.arccos(np.clip(ak.to_numpy(momentum_z), -1.0, 1.0)))
    return angle, ak.to_numpy(energy_kev) / 1000.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=1000)
    parser.add_argument("-o", "--output", default="gold_foil_python_results.csv")
    parser.add_argument("--seed", type=int, default=137)
    parser.add_argument(
        "--batch",
        action="store_true",
        help="run the requested events and write a CSV instead of opening the Qt viewer",
    )
    args = parser.parse_args()

    with g4.Application(gdml=GOLD_FOIL_GDML, seed=args.seed) as app:
        app.set_event_fields(
            {
                "id",
                "track_id",
                "track_particle",
                "step_volume",
                "step_volume_post",
                "step_momentum",
                "step_track_kinetic_energy",
            }
        )
        # /gun/ commands: energy in MeV, position in cm (PrimaryGeneratorAction.cpp)
        app._send_and_recv(Message("generator", "set_particle", ("alpha",), {}))
        app._send_and_recv(Message("generator", "set_energy", (5.5,), {}))
        app._send_and_recv(Message("generator", "set_position", ([0.0, 0.0, -5.0],), {}))
        app._send_and_recv(Message("generator", "set_direction", ([0.0, 0.0, 1.0],), {}))

        if not args.batch:
            if not app.visualization_available():
                raise RuntimeError(
                    "This installation was built without Qt visualization support. "
                    "Reinstall geant4-python-application with "
                    "GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON."
                )
            print("Opening the Qt viewer. In its command panel, run: /run/beamOn 100")
            app.visualize(
                [
                    "/vis/open OGL",
                    "/vis/drawVolume",
                    "/vis/viewer/set/style wireframe",
                    "/vis/scene/add/trajectories smooth",
                    "/tracking/storeTrajectory 1",
                    "/vis/scene/endOfEventAction accumulate 100",
                ]
            )
            return

        events = app.run(args.events)

    angle, energy = scattering(events)

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["event_id", "scattering_angle_deg", "exit_energy_MeV"])
        writer.writerows(zip(range(len(angle)), angle, energy))

    print(f"events simulated : {len(events)}")
    print(f"alphas exiting   : {len(angle)}")
    print(f"angle  mean/max  : {angle.mean():.4f} / {angle.max():.4f} deg")
    print(f"energy mean      : {energy.mean():.4f} MeV (from 5.5 MeV)")
    print(f"scattered >1 deg : {(angle > 1).sum()}  >5 deg: {(angle > 5).sum()}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
