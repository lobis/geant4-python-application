# Geant4 Python Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lobis/geant4-python-application/HEAD)
[![Wheels](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml)
[![Build and Test](https://github.com/lobis/geant4-python-application/actions/workflows/build-test.yaml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/test.yaml)

This is an experiment at providing a pythonic interface to Geant4.

The goal is not to provide a full python interface to Geant4, but rather to
provide a high-level interface to a generic Geant4 application which is highly
configurable.

If you are looking for a full set of python bindings for Geant4, I recommend
looking at [geant4_pybind](https://github.com/HaarigerHarald/geant4_pybind).

## Overview

- Configurable Geant4 application written in C++
- Python interface to the application via
  [pybind11](https://github.com/pybind/pybind11)
- The complete event data is available as an
  [awkward array](https://github.com/scikit-hep/awkward)

New to Geant4 or this package? See the
[Python developer guide](PYTHON_DEVELOPER_GUIDE.md).

## Platform support

Tested on macOS and Ubuntu; still undergoing broader testing. If you hit a
bug, please report it via [GitHub Issues](https://github.com/lobis/geant4-python-application/issues)
or reach out to kavyavadhwa@gmail.com.

## Installation

```bash
pip install geant4-python-application
```

No system Geant4 install is required — the wheel is statically linked.
Physics data files download automatically on first use.

Building from source, Qt visualization, the relocatable macOS wheel, and data
file management are covered in [INSTALLATION.md](INSTALLATION.md).

## Usage

```python
import geant4_python_application as g4

# Use a temporary directory for the Geant4 data files (remove this line to use the default location)
g4.application_directory(temp=True)

with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
    events = app.run(n_events=100)

print(events)
```

A Geant4 reference physics list can be selected by name:

```python
with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT") as app:
    events = app.run(100)

print(g4.Application.available_physics_lists())
```

Particle guns and Geant4's General Particle Source have a Python interface:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.generator.use_gps().particle("gamma").energy(2, "MeV")
    app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
    events = app.run(100)
```

Advanced GPS distributions remain accessible through
`app.generator.commands(["/gps/pos/type Plane", ...])`.

Optical physics and uniform global magnetic/electric fields can be enabled directly:

```python
with g4.Application(gdml=my_optical_gdml, optical=True) as app:
    app.detector.magnetic_field = (0.0, 0.0, 1.5)  # tesla
    app.detector.electric_field = (0.0, 0.0, 0.5)  # kV/cm
    events = app.run(100)
```

Optical scintillator GDML + tuning helpers:

```python
from geant4_python_application import optical as gopt

with g4.Application(gdml=gopt.optical_water_gdml, optical=True) as app:
    app.commands(gopt.scintillation_commands(yield_factor=1.0))
    events = app.run(100)  # track.particle contains 'opticalphoton'
```

Recorded steps can be scored per event or into a Cartesian energy mesh:

```python
energy_per_event = g4.Scoring.energy_deposit(events, volume="detector")
mesh, edges = g4.Scoring.energy_mesh(events, bins=(20, 20, 40))
```

Python run/event/track/step callbacks (offline over awkward arrays):

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    events = app.run_with_callbacks(
        100, on_run=lambda evs: print(len(evs)),
        on_event=lambda ev: None, on_track=lambda tr, ev: None,
        on_step=lambda st, tr, ev: None,
    )
```

Extra physics constructors incl. DNA, CAD/VTK/ROOT/HepMC, and MPI splitting:

```python
print(g4.Application.available_extra_physics())
with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT") as app:
    app.add_physics("G4EmDNAPhysics_option2")  # or G4EmExtraPhysics, G4OpticalPhysics...
    events = app.run(100)

from geant4_python_application import cad, io as gio, distributed as dist

gdml = cad.mesh_to_gdml(*cad.cube_mesh(100.0))  # or cad.stl_ascii_to_gdml(stl_text)
gio.mesh_to_vtk(mesh, edges, "mesh.vtk")
gio.events_to_parquet(events, "events.parquet")
gio.events_to_root(events, "events.root")  # needs uproot
primaries = gio.hepmc_to_primaries(open("events.hepmc").read())

rank, size = dist.get_rank_size()
start, count = dist.split_count(1000, rank, size)  # mpiexec -n 2 python run.py
```

### Interactive Qt visualization

When the extension is built against a Geant4 installation with Qt and OpenGL,
enable visualization at install time:

```bash
pip install . -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON
```

Then open Geant4's interactive Qt viewer. The call returns when the window is
closed, and commands can be entered in the viewer's command panel:

```python
import geant4_python_application as g4

with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
    app.command("/gun/particle e-")
    app.command("/gun/energy 100 MeV")
    app.visualize()
```
