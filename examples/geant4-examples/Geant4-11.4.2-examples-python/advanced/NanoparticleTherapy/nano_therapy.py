"""Targeted cancer therapy with nanoparticles (assignment).

Photon beam irradiates a water phantom containing a tissue tumour.
The tumour contains a gold cluster representing targeted gold
nanoparticles (Au, Z=79). kV photons undergo enhanced photoelectric
absorption in gold -> photo/Auger electrons -> local dose enhancement.

Runs twice (--batch): with Au and without Au (cluster = tissue),
then reports deposited energy, estimated dose, and Dose Enhancement
Ratio: DER = Dose_tumour(Au) / Dose_tumour(no Au).

Geometry (nested, no overlaps):
  World (G4_AIR, box) -> Phantom (G4_WATER, box 90 mm)
    -> Tumour (G4_A-150_TISSUE, sphere r=15 mm)
      -> NanoCluster (G4_Au or tissue, sphere r=5 mm)
"""

from __future__ import annotations

import argparse
import math

import awkward as ak
import geant4_python_application as g4

# Densities (g/cm3) for dose = energy / mass estimates.
DENSITY = {"Phantom": 1.0, "Tumor": 1.127, "NanoCluster_Au": 19.32, "NanoCluster_tissue": 1.127}
KEV_TO_JOULE = 1.602176634e-16


def geometry(with_gold: bool = True) -> str:
    cluster_mat = "G4_Au" if with_gold else "G4_A-150_TISSUE"
    return f'''<?xml version="1.0" encoding="utf-8"?>
<gdml><solids>
  <box name="WorldSolid" x="200" y="200" z="200" lunit="mm"/>
  <box name="PhantomSolid" x="90" y="90" z="90" lunit="mm"/>
  <sphere name="TumorSolid" rmin="0" rmax="15" startphi="0" deltaphi="360"
    starttheta="0" deltatheta="180" aunit="deg" lunit="mm"/>
  <sphere name="ClusterSolid" rmin="0" rmax="5" startphi="0" deltaphi="360"
    starttheta="0" deltatheta="180" aunit="deg" lunit="mm"/>
</solids><structure>
  <volume name="NanoClusterLV"><materialref ref="{cluster_mat}"/><solidref ref="ClusterSolid"/></volume>
  <volume name="TumorLV"><materialref ref="G4_A-150_TISSUE"/><solidref ref="TumorSolid"/>
    <physvol name="NanoCluster"><volumeref ref="NanoClusterLV"/></physvol>
  </volume>
  <volume name="PhantomLV"><materialref ref="G4_WATER"/><solidref ref="PhantomSolid"/>
    <physvol name="Tumor"><volumeref ref="TumorLV"/></physvol>
  </volume>
  <volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldSolid"/>
    <physvol name="Phantom"><volumeref ref="PhantomLV"/></physvol>
  </volume>
</structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


def run_case(events_n: int, with_gold: bool) -> dict[str, float]:
    """Run one configuration, return deposited energy (keV) per region."""
    with g4.Application(gdml=geometry(with_gold), seed=137) as app:
        app.set_event_fields({"id", "step_energy", "step_volume"})
        app.commands([
            "/gun/particle gamma", "/gun/energy 100 keV",
            "/gun/position 0 0 -10 cm", "/gun/direction 0 0 1",
        ])
        events = app.run(events_n)

    energy = events.track.step.energy
    volume = events.track.step.volume
    out = {}
    for region in ("Phantom", "Tumor", "NanoCluster"):
        out[region] = float(ak.sum(energy[volume == region]))
    out["TumorTotal"] = out["Tumor"] + out["NanoCluster"]
    return out


def dose_gy(energy_kev: float, mass_g: float) -> float:
    return energy_kev * KEV_TO_JOULE / (mass_g * 1e-3)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=1000)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()

    if not args.batch:
        with g4.Application(gdml=geometry(with_gold=True), seed=137) as app:
            app.commands([
                "/gun/particle gamma", "/gun/energy 100 keV",
                "/gun/position 0 0 -10 cm", "/gun/direction 0 0 1",
            ])
            app.visualize([
                "/vis/open OGL", "/vis/drawVolume",
                "/vis/viewer/set/background black",
                "/vis/viewer/set/style surface",
                # colour-code by logical volume: phantom=blue, tumour=green, Au=red
                "/vis/geometry/set/colour World 1 1 1 0",
                "/vis/geometry/set/colour PhantomLV 0 0.3 1 0.15",
                "/vis/geometry/set/colour TumorLV 0 1 0 0.35",
                "/vis/geometry/set/colour NanoClusterLV 1 0 0 1",
                # colour-code tracks: gamma=yellow, e-=red, rest=white
                "/vis/modeling/trajectories/create/drawByParticleID",
                "/vis/modeling/trajectories/drawByParticleID-0/set gamma yellow",
                "/vis/modeling/trajectories/drawByParticleID-0/set e- red",
                "/vis/modeling/trajectories/drawByParticleID-0/set e+ blue",
                "/vis/scene/add/trajectories smooth", "/tracking/storeTrajectory 1",
                "/vis/scene/endOfEventAction accumulate 100",
            ])
            return

    # Volumes/masses: cluster r=5mm, tumour r=15mm, phantom 90mm box.
    v_cluster = 4 / 3 * math.pi * 0.5**3  # cm3
    v_tumor = 4 / 3 * math.pi * 1.5**3 - v_cluster
    v_phantom = 9.0**3 - 4 / 3 * math.pi * 1.5**3
    masses = {"Phantom": v_phantom * DENSITY["Phantom"],
              "Tumor": v_tumor * DENSITY["Tumor"]}

    no_au = run_case(args.events, with_gold=False)
    with_au = run_case(args.events, with_gold=True)
    masses_au = dict(masses, NanoCluster=v_cluster * DENSITY["NanoCluster_Au"])
    masses_no = dict(masses, NanoCluster=v_cluster * DENSITY["NanoCluster_tissue"])

    print(f"events per case: {args.events}, beam: 100 keV gamma")
    for label, res, m in (("no-Au ", no_au, masses_no), ("with-Au", with_au, masses_au)):
        print(f"[{label}] Phantom(healthy): {res['Phantom']:.1f} keV "
              f"({dose_gy(res['Phantom'], m['Phantom']):.3e} Gy) | "
              f"Tumor rim: {res['Tumor']:.1f} keV | "
              f"Cluster: {res['NanoCluster']:.1f} keV | "
              f"TumorTotal: {res['TumorTotal']:.1f} keV")

    der = with_au["TumorTotal"] / no_au["TumorTotal"] if no_au["TumorTotal"] else float("nan")
    print(f"Dose Enhancement Ratio (TumorTotal Au / no-Au): {der:.3f}")
    print("Assignment: explain why DER>1 (photoelectric ~ Z^3/E^3 in Au), "
          "why 100 keV shows it but MV beam would show less, and what the "
          "Phantom dose says about healthy-tissue sparing.")


if __name__ == "__main__":
    main()
