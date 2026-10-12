# Geant4 Python Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lobis/geant4-python-application/HEAD?labpath=examples%2Fattenuation.ipynb)
[![Binder](https://binderhub.ssl-hep.org/badge_logo.svg)](https://binderhub.ssl-hep.org/v2/gh/lobis/geant4-python-application/HEAD?labpath=examples%2Fattenuation.ipynb)

[![PyPI](https://img.shields.io/pypi/v/geant4-python-application)](https://pypi.org/project/geant4-python-application/)
[![Python](https://img.shields.io/pypi/pyversions/geant4-python-application)](https://pypi.org/project/geant4-python-application/)
[![Wheels](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml)
[![Build and Test](https://github.com/lobis/geant4-python-application/actions/workflows/build-test.yaml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/build-test.yaml)

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
[Python developer guide](https://github.com/lobis/geant4-python-application/blob/main/PYTHON_DEVELOPER_GUIDE.md).

## Platform support

Tested on macOS and Ubuntu; still undergoing broader testing. If you hit a bug,
please report it via
[GitHub Issues](https://github.com/lobis/geant4-python-application/issues) or
reach out to kavyavadhwa@gmail.com.

## Installation

The package is published on
[PyPI](https://pypi.org/project/geant4-python-application/). Install it into a
fresh virtual environment: mixing it with packages already in your system or
base conda Python (other Qt/PyQt, numpy or Geant4 builds) is the most common
cause of library mismatch errors.

```bash
python3 -m venv g4-env
source g4-env/bin/activate
python -m pip install --upgrade pip
pip install "geant4-python-application[gui]"
```

With conda, create a new environment instead of using `base`:

```bash
conda create -n g4 python=3.12 -y
conda activate g4
pip install "geant4-python-application[gui]"
```

Activate the environment again (`source g4-env/bin/activate` or
`conda activate g4`) in every new terminal before using the package.

- Prebuilt wheels for macOS (Apple Silicon and Intel) and Linux x86_64, Python
  3.8–3.13. Geant4 is bundled, so no separate Geant4 (C++) installation is
  needed.
- `[gui]` adds the interactive Qt viewer (`app.visualize()`); leave it out for a
  physics-only install.
- Check the installation:

  ```bash
  python -c "import geant4_python_application as g4; print(g4.__version__)"
  ```

- The first simulation downloads Geant4's data files (~2 GB) once per user, to
  `~/Library/Application Support/geant4_python_application` (macOS) or
  `~/.local/share/geant4_python_application` (Linux). Set
  `GEANT4_PYTHON_APPLICATION_DIR` to use another location.
- Windows, Linux aarch64, building from source and data file management are
  covered in
  [INSTALLATION.md](https://github.com/lobis/geant4-python-application/blob/main/INSTALLATION.md).
  On Windows, WSL works with the Linux wheels.

The examples are not part of the package; run them from a clone of the
repository:

```bash
git clone https://github.com/lobis/geant4-python-application
cd geant4-python-application
python examples/geant4-examples/Geant4-11.4.2-examples-python/basic/B1/b1.py --batch -n 10
```

`--batch` runs headless; drop it to open the Qt viewer.

## Usage

```python
import geant4_python_application as g4

with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
    events = app.run(100)

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

Optical physics and uniform global magnetic/electric fields can be enabled
directly:

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
        100,
        on_run=lambda evs: print(len(evs)),
        on_event=lambda ev: None,
        on_track=lambda tr, ev: None,
        on_step=lambda st, tr, ev: None,
    )
```

Extra physics constructors incl. DNA, CAD/VTK/ROOT/HepMC, and MPI splitting:

```python
print(g4.Application.available_extra_physics())
with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT") as app:
    app.add_physics(
        "G4EmDNAPhysics_option2"
    )  # or G4EmExtraPhysics, G4OpticalPhysics...
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

Install with the `gui` extra (`pip install "geant4-python-application[gui]"`),
or for source builds see
[INSTALLATION.md](https://github.com/lobis/geant4-python-application/blob/main/INSTALLATION.md).
Then open Geant4's interactive Qt viewer. The call returns when the window is
closed, and commands can be entered in the viewer's command panel:

```python
import geant4_python_application as g4

with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
    app.command("/gun/particle e-")
    app.command("/gun/energy 100 MeV")
    app.visualize()
```
