from __future__ import annotations

import awkward as ak
import numpy as np

import geant4_python_application as g4
from geant4_python_application import cad
from geant4_python_application import distributed as dist
from geant4_python_application import io as gio
from geant4_python_application import optical as opt


def test_electric_field():
    with g4.Application(gdml=g4.basic_gdml, seed=101) as app:
        app.detector.magnetic_field = (0.0, 0.0, 1.0)
        app.detector.electric_field = (0.0, 0.0, 0.5)
        assert tuple(app.detector.magnetic_field) == (0.0, 0.0, 1.0)
        assert tuple(app.detector.electric_field) == (0.0, 0.0, 0.5)
        app.command("/gun/particle e-")
        app.command("/gun/energy 5 MeV")
        assert len(app.run(2)) == 2


def test_optical_scintillation():
    with g4.Application(gdml=opt.optical_water_gdml, optical=True, seed=102) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 10 MeV")
        app.command("/gun/position 0 0 0 mm")
        app.command("/gun/direction 1 0 0")
        events = app.run(2)
        assert len(events) == 2
        parts = set(ak.to_list(ak.flatten(events.track.particle, axis=None)))
        assert "opticalphoton" in parts
    assert len(opt.scintillation_commands()) == 2


def test_lxe_and_wls_optical_materials():
    for gdml, particle, energy in (
        (opt.lxe_scintillator_gdml, "e-", "1 MeV"),
        (opt.wls_fiber_gdml, "opticalphoton", "3.5 eV"),
    ):
        with g4.Application(gdml=gdml, optical=True, seed=110) as app:
            app.command(f"/gun/particle {particle}")
            app.command(f"/gun/energy {energy}")
            app.command("/gun/position 0 0 0 mm")
            app.command("/gun/direction 0 0 1")
            events = app.run(1)
        particles = ak.flatten(events.track.particle, axis=None)
        assert bool(ak.any(particles == "opticalphoton"))


def test_expanded_parameterised_geometry():
    gdml = g4.geometry.linear_array_gdml(5, spacing_mm=15, box_size_mm=5)
    assert gdml.count('<physvol name="cell_') == 5
    with g4.Application(gdml=gdml, seed=111) as app:
        app.command("/gun/particle geantino")
        app.command("/gun/position -45 0 0 mm")
        app.command("/gun/direction 1 0 0")
        assert len(app.run(1)) == 1


def test_callbacks():
    counts = {"run": 0, "event": 0, "track": 0, "step": 0}
    with g4.Application(gdml=g4.basic_gdml, seed=103) as app:
        app.command("/gun/particle gamma")
        app.command("/gun/energy 1 MeV")
        events = app.run_with_callbacks(
            2,
            on_run=lambda evs: counts.__setitem__("run", counts["run"] + 1),
            on_event=lambda ev: counts.__setitem__("event", counts["event"] + 1),
            on_track=lambda tr, ev: counts.__setitem__("track", counts["track"] + 1),
            on_step=lambda st, tr, ev: counts.__setitem__("step", counts["step"] + 1),
        )
        assert len(events) == 2
    assert counts == {"run": 1, "event": 2, "track": counts["track"], "step": counts["step"]}
    assert counts["track"] > 0 and counts["step"] > 0


def test_extra_physics_and_dna():
    assert "G4EmExtraPhysics" in g4.Application.available_extra_physics()
    assert any("DNA" in x for x in g4.Application.available_extra_physics())
    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=104) as app:
        app.add_physics("G4EmExtraPhysics")
        app.command("/gun/particle gamma")
        app.command("/gun/energy 1 MeV")
        assert len(app.run(1)) == 1
    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=105) as app:
        app.add_physics("G4EmDNAPhysics_option2")
        app.command("/gun/particle e-")
        app.command("/gun/energy 100 keV")
        assert len(app.run(1)) == 1


def test_cad_vtk_parquet_hepmc(tmp_path):
    v, f = cad.cube_mesh(100.0)
    gdml = cad.mesh_to_gdml(v, f)
    assert "tessellated" in gdml
    with g4.Application(gdml=gdml, seed=106) as app:
        assert len(app.run(1)) == 1
    with g4.Application(gdml=g4.basic_gdml, seed=107) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 5 MeV")
        events = app.run(2)
    mesh, edges = g4.Scoring.energy_mesh(events, bins=(3, 3, 3))
    vtk_path = gio.mesh_to_vtk(mesh, edges, tmp_path / "mesh.vtk")
    assert "STRUCTURED_POINTS" in vtk_path.read_text()[:500]
    pq = gio.events_to_parquet(events, tmp_path / "events.parquet")
    assert len(gio.events_from_parquet(pq)) == len(events)
    hepmc = "E 0 1 1\nP 1 22 0 0 1 1 0 1\nP 2 11 0.1 0 0.5 0.6 0.0005 1\n"
    prim = gio.hepmc_to_primaries(hepmc)
    assert len(prim) == 2


def test_root_io(tmp_path):
    uproot = __import__("importlib").util.find_spec("uproot")
    if uproot is None:
        return
    with g4.Application(gdml=g4.basic_gdml, seed=108) as app:
        app.command("/gun/particle gamma")
        app.command("/gun/energy 1 MeV")
        events = app.run(2)
    rp = gio.events_to_root(events, tmp_path / "events.root")
    assert rp.exists()
    assert len(gio.events_from_root(rp)["id"]) == len(events)


def test_distributed_split():
    assert dist.get_rank_size() == (0, 1)
    assert dist.split_count(10, 0, 2) == (0, 5)
    assert dist.split_count(10, 1, 2) == (5, 5)
    s0, c0 = dist.split_count(3, 0, 2)
    _, c1 = dist.split_count(3, 1, 2)
    assert c0 + c1 == 3
    assert s0 == 0


def test_native_scoring_mesh(tmp_path):
    with g4.Application(gdml=g4.basic_gdml, seed=109) as app:
        mesh = g4.NativeScoringMesh(app, "testMesh", "edep")
        mesh.box((250, 250, 250), (2, 2, 2))
        app.command("/gun/particle e-")
        app.command("/gun/energy 1 MeV")
        app.run(1)
        output = mesh.dump(tmp_path / "mesh.csv")
    assert output.exists()
    assert output.stat().st_size > 0
