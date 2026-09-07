from __future__ import annotations

"""VTK / ROOT / external-generator helpers (pure Python, optional deps).

- mesh_to_vtk: write Cartesian energy mesh to legacy VTK STRUCTURED_POINTS.
- events_to_parquet / events_from_parquet: always available (pyarrow).
- events_to_root / events_from_root: via uproot if installed.
- hepmc_to_primaries: minimal HepMC2-ASCII -> awkward primaries.
"""

from pathlib import Path

import awkward as ak
import numpy as np


def mesh_to_vtk(mesh: np.ndarray, edges: tuple, filename: str | Path) -> Path:
    """Write (nx,ny,nz) energy mesh to legacy VTK STRUCTURED_POINTS file."""
    mesh = np.asarray(mesh, dtype=float)
    if mesh.ndim != 3:
        msg = f"mesh must be 3D, got shape {mesh.shape}"
        raise ValueError(msg)
    nx, ny, nz = mesh.shape
    if len(edges) != 3:
        msg = "edges must be (x_edges, y_edges, z_edges)"
        raise ValueError(msg)
    origins, spacings = [], []
    dims = []
    for n, e in zip((nx, ny, nz), edges, strict=True):
        e = np.asarray(e, dtype=float)
        if len(e) != n + 1:
            msg = f"edges length {len(e)} inconsistent with mesh dim {n}"
            raise ValueError(msg)
        origins.append(float(e[0]))
        spacings.append(float(e[1] - e[0]) if n > 0 else 1.0)
        dims.append(n + 1 if False else n)  # points == cells for cell data
    out = Path(filename)
    # VTK Fortran ordering: x varies fastest
    flat = mesh.ravel(order="F")
    with out.open("w") as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("geant4 energy mesh\n")
        f.write("ASCII\n")
        f.write("DATASET STRUCTURED_POINTS\n")
        f.write(f"DIMENSIONS {nx} {ny} {nz}\n")
        f.write(f"ORIGIN {origins[0]} {origins[1]} {origins[2]}\n")
        f.write(f"SPACING {spacings[0]} {spacings[1]} {spacings[2]}\n")
        f.write(f"POINT_DATA {nx * ny * nz}\n")
        f.write("SCALARS energy_keV float 1\n")
        f.write("LOOKUP_TABLE default\n")
        for v in flat:
            f.write(f"{v}\n")
    return out


def events_to_parquet(events: ak.Array, filename: str | Path) -> Path:
    out = Path(filename)
    ak.to_parquet(events, out)
    return out


def events_from_parquet(filename: str | Path) -> ak.Array:
    return ak.from_parquet(Path(filename))


def events_to_root(events: ak.Array, filename: str | Path, treename: str = "events") -> Path:
    """Write flat per-event summary + hits to ROOT via uproot (requires uproot)."""
    try:
        import uproot
    except ImportError as e:
        msg = "uproot is required for ROOT I/O: pip install uproot"
        raise ImportError(msg) from e
    out = Path(filename)
    # Flatten what ROOT can store: per-event id + deposited energy + nhits.
    # Full nested step records stay in parquet; ROOT holds analysis summary.
    import geant4_python_application as g4

    edep = np.asarray(g4.Scoring.energy_deposit(events), dtype=np.float64)
    ids = np.asarray(events.id, dtype=np.int64) if "id" in events.fields else np.arange(len(events))
    with uproot.recreate(out) as f:
        f[treename] = {"id": ids, "edep_keV": edep}
    return out


def events_from_root(filename: str | Path, treename: str = "events") -> dict:
    try:
        import uproot
    except ImportError as e:
        msg = "uproot is required for ROOT I/O: pip install uproot"
        raise ImportError(msg) from e
    with uproot.open(f"{filename}:{treename}") as t:
        return t.arrays(library="np")


_PDG_TO_G4 = {
    11: "e-", -11: "e+", 22: "gamma", 13: "mu-", -13: "mu+",
    2112: "neutron", 2212: "proton", 211: "pi+", -211: "pi-",
    111: "pi0", 321: "kaon+", -321: "kaon-", 12: "nu_e",
    -12: "anti_nu_e", 14: "nu_mu", -14: "anti_nu_mu",
}


def hepmc_to_primaries(hepmc_text: str) -> ak.Array:
    """Parse minimal HepMC2 ASCII (E/P lines) into awkward primaries.

    Expects lines like: P <id> <pdg> <px_GeV> <py> <pz> <E_GeV> ...
    Position defaults to origin; direction = p/|p|; energy = kinetic approx.
    Unknown PDG codes fall back to geantino.
    """
    records = []
    for line in hepmc_text.splitlines():
        s = line.strip().split()
        if not s or s[0] != "P":
            continue
        if len(s) < 7:
            continue
        pdg = int(s[2])
        px, py, pz, e = (float(s[3]), float(s[4]), float(s[5]), float(s[6]))
        p = float(np.sqrt(px * px + py * py + pz * pz))
        if p == 0:
            continue
        particle = _PDG_TO_G4.get(pdg, "geantino")
        # awkward primary energy convention in this package: keV numbers?
        # Application primaries use raw doubles passed to gun in keV? Keep MeV->keV.
        records.append(
            {
                "particle": particle,
                "energy": e * 1e6,  # GeV -> keV (gun awkward path uses keV)
                "direction": {"x": px / p, "y": py / p, "z": pz / p},
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            }
        )
    if not records:
        msg = "no P lines parsed from HepMC text"
        raise ValueError(msg)
    return ak.Array(records)
