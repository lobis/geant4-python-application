"""Brain tumour reduction via targeted Au-nanoparticle therapy (assignment).

Geant4 cannot shrink a tumour - it scores DOSE. Reduction is inferred:
  dose -> cell survival (Linear-Quadratic) -> volume reduction estimate.

Geometry (nested spheres, no overlaps):
  World (G4_AIR) -> Skull (G4_BONE_COMPACT_ICRU, r=85mm)
    -> Brain (G4_BRAIN_ICRP, r=78mm)
      -> Tumor (G4_A-150_TISSUE, r=12mm at x=20mm,z=10mm)
        -> NanoCluster (G4_Au or tissue, r=4mm, Au = targeted nanoparticles)

Beam: 100 keV gammas aimed at tumour. Runs with/without Au (--batch),
reports DER, scaled clinical dose (2 Gy fraction), survival S=exp(-aD-bD^2),
and inferred reduction = 1-S.
"""

from __future__ import annotations

import argparse
import math

import awkward as ak
import geant4_python_application as g4

DENSITY = {"Skull": 1.85, "Brain": 1.03, "Tumor": 1.127,
           "ClusterAu": 19.32, "ClusterTissue": 1.127}
KEV_TO_J = 1.602176634e-16
TX, TZ = 20.0, 10.0  # tumour centre (mm)
ALPHA, BETA = 0.3, 0.03  # /Gy, glioma-like LQ params


def geometry(with_gold: bool = True) -> str:
    cluster_mat = "G4_Au" if with_gold else "G4_A-150_TISSUE"
    return f'''<?xml version="1.0" encoding="utf-8"?>
<gdml><solids>
  <box name="WorldSolid" x="300" y="300" z="300" lunit="mm"/>
  <sphere name="SkullSolid" rmin="0" rmax="85" startphi="0" deltaphi="360"
    starttheta="0" deltatheta="180" aunit="deg" lunit="mm"/>
  <sphere name="BrainSolid" rmin="0" rmax="78" startphi="0" deltaphi="360"
    starttheta="0" deltatheta="180" aunit="deg" lunit="mm"/>
  <sphere name="TumorSolid" rmin="0" rmax="12" startphi="0" deltaphi="360"
    starttheta="0" deltatheta="180" aunit="deg" lunit="mm"/>
  <sphere name="ClusterSolid" rmin="0" rmax="4" startphi="0" deltaphi="360"
    starttheta="0" deltatheta="180" aunit="deg" lunit="mm"/>
</solids><structure>
  <volume name="NanoClusterLV"><materialref ref="{cluster_mat}"/><solidref ref="ClusterSolid"/></volume>
  <volume name="TumorLV"><materialref ref="G4_A-150_TISSUE"/><solidref ref="TumorSolid"/>
    <physvol name="NanoCluster"><volumeref ref="NanoClusterLV"/></physvol>
  </volume>
  <volume name="BrainLV"><materialref ref="G4_BRAIN_ICRP"/><solidref ref="BrainSolid"/>
    <physvol name="Tumor"><volumeref ref="TumorLV"/>
      <position unit="mm" x="{TX}" y="0" z="{TZ}"/></physvol>
  </volume>
  <volume name="SkullLV"><materialref ref="G4_BONE_COMPACT_ICRU"/><solidref ref="SkullSolid"/>
    <physvol name="Brain"><volumeref ref="BrainLV"/></physvol>
  </volume>
  <volume name="World"><materialref ref="G4_AIR"/><solidref ref="WorldSolid"/>
    <physvol name="Skull"><volumeref ref="SkullLV"/></physvol>
  </volume>
</structure><setup name="Default" version="1.0"><world ref="World"/></setup></gdml>'''


GUN = ["/gun/particle gamma", "/gun/energy 100 keV",
       f"/gun/position {TX / 10} 0 -12 cm", "/gun/direction 0 0 1"]


def run_case(n: int, with_gold: bool) -> dict[str, float]:
    with g4.Application(gdml=geometry(with_gold), seed=137) as app:
        app.set_event_fields({"id", "step_energy", "step_volume"})
        app.commands(GUN)
        events = app.run(n)
    e, v = events.track.step.energy, events.track.step.volume
    out = {r: float(ak.sum(e[v == r])) for r in ("Skull", "Brain", "Tumor", "NanoCluster")}
    out["TumorTotal"] = out["Tumor"] + out["NanoCluster"]
    return out


def dose_gy(kev: float, mass_g: float) -> float:
    return kev * KEV_TO_J / (mass_g * 1e-3)


def survival(dose: float) -> float:
    return math.exp(-ALPHA * dose - BETA * dose * dose)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", "--events", type=int, default=1000)
    p.add_argument("--batch", action="store_true")
    args = p.parse_args()

    if not args.batch:
        with g4.Application(gdml=geometry(True), seed=137) as app:
            app.commands(GUN)
            app.visualize([
                "/vis/open OGL", "/vis/drawVolume",
                "/vis/viewer/set/background black",
                "/vis/viewer/set/style surface",
                "/vis/geometry/set/colour World 1 1 1 0",
                "/vis/geometry/set/colour SkullLV 0.9 0.8 0.5 0.12",
                "/vis/geometry/set/colour BrainLV 1 0.5 0.7 0.18",
                "/vis/geometry/set/colour TumorLV 0 1 0 0.5",
                "/vis/geometry/set/colour NanoClusterLV 1 0 0 1",
                "/vis/modeling/trajectories/create/drawByParticleID",
                "/vis/modeling/trajectories/drawByParticleID-0/set gamma yellow",
                "/vis/modeling/trajectories/drawByParticleID-0/set e- red",
                "/vis/modeling/trajectories/drawByParticleID-0/set e+ blue",
                "/vis/scene/add/trajectories smooth", "/tracking/storeTrajectory 1",
                "/vis/scene/endOfEventAction accumulate 100",
            ])
            return

    v_cl = 4 / 3 * math.pi * 0.4**3
    v_tu = 4 / 3 * math.pi * 1.2**3 - v_cl
    v_br = 4 / 3 * math.pi * 7.8**3 - 4 / 3 * math.pi * 1.2**3
    v_sk = 4 / 3 * math.pi * 8.5**3 - 4 / 3 * math.pi * 7.8**3
    m = {"Brain": v_br * DENSITY["Brain"], "Tumor": v_tu * DENSITY["Tumor"],
         "Skull": v_sk * DENSITY["Skull"]}

    no, yes = run_case(args.events, False), run_case(args.events, True)
    der = yes["TumorTotal"] / no["TumorTotal"] if no["TumorTotal"] else float("nan")

    # Scale: give no-Au tumour a clinical 2 Gy fraction; same fluence with Au gives 2*DER.
    s_no, s_au = survival(2.0), survival(2.0 * der)
    print(f"events: {args.events}, beam 100 keV -> tumour at ({TX},0,{TZ}) mm")
    print(f"[no-Au ] TumorTotal {no['TumorTotal']:.1f} keV | Brain {no['Brain']:.1f} keV | Skull {no['Skull']:.1f} keV")
    print(f"[with-Au] TumorTotal {yes['TumorTotal']:.1f} keV | Brain {yes['Brain']:.1f} keV | Skull {yes['Skull']:.1f} keV")
    print(f"DER (tumour Au/no-Au): {der:.2f}")
    print(f"At 2 Gy to tumour without Au: survival {s_no:.3f} (reduction {(1 - s_no) * 100:.1f}%)")
    print(f"Same fluence with Au -> {2 * der:.1f} Gy: survival {s_au:.3e} (reduction {(1 - s_au) * 100:.2f}%)")
    print("Report: Geant4 proves DOSE boost (photoelectric in Au Z=79); "
          "reduction % comes from LQ model, not from cells dying in code. "
          "Solid AuSphere exaggerates (real DER 1.1-2); skull/brain doses show sparing.")


if __name__ == "__main__":
    main()
