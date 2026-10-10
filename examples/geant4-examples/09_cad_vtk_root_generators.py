"""09 - CAD, VTK, ROOT and external generators.

Shows: CAD mesh -> GDML (tessellated), energy mesh -> VTK, events ->
parquet/ROOT, HepMC-ASCII -> primaries. Writes to /tmp.
Run: python 09_cad_vtk_root_generators.py
"""
from __future__ import annotations


def main() -> None:
    import sys
    from pathlib import Path

    import geant4_python_application as g4
    from geant4_python_application import cad
    from geant4_python_application import io as gio

    # CAD: cube mesh -> GDML -> run 1 event
    vertices, faces = cad.cube_mesh(100.0)
    gdml = cad.mesh_to_gdml(vertices, faces)
    assert "tessellated" in gdml
    print(f"CAD cube: {len(vertices)} vertices, {len(faces)} triangles")
    with g4.Application(gdml=gdml, seed=20) as app:
        print(f"CAD GDML ran {len(app.run(1))} event")

    # ASCII STL -> GDML (parse-only check)
    stl = (
        "solid c\nfacet normal 0 0 1\nouter loop\n"
        "vertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\n"
        "endloop\nendfacet\nendsolid c\n"
    )
    assert "tessellated" in cad.stl_ascii_to_gdml(stl)
    print("STL parse OK")

    # Physics run for I/O demos
    with g4.Application(gdml=g4.basic_gdml, seed=21) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 5 MeV")
        events = app.run(2)

    # VTK
    mesh, edges = g4.Scoring.energy_mesh(events, bins=(3, 3, 3))
    vtk_path = gio.mesh_to_vtk(mesh, edges, Path("/tmp/g4_example_mesh.vtk"))
    print(f"VTK written: {vtk_path}")

    # Parquet round-trip (always available via pyarrow)
    pq = gio.events_to_parquet(events, Path("/tmp/g4_example_events.parquet"))
    assert len(gio.events_from_parquet(pq)) == len(events)
    print(f"parquet round-trip OK: {pq}")

    # ROOT via uproot (pip install uproot if missing)
    try:
        rp = gio.events_to_root(events, Path("/tmp/g4_example_events.root"))
        back = gio.events_from_root(rp)
        assert len(back["id"]) == len(events)
        print(f"ROOT round-trip OK: {rp}")
    except ImportError as exc:
        print(f"ROOT skipped: {exc}")

    # External generator: minimal HepMC2-ASCII -> awkward primaries
    hepmc = "E 0 1 1\nP 1 22 0 0 1 1 0 1\nP 2 11 0.1 0 0.5 0.6 0.0005 1\n"
    primaries = gio.hepmc_to_primaries(hepmc)
    print(f"HepMC primaries: {list(primaries.particle)}")

    if "--vis" in sys.argv:
        with g4.Application(gdml=gdml, seed=20) as app:
            app.command("/gun/particle e-")
            app.command("/gun/energy 5 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
