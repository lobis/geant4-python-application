# Geant4 with Python: a beginner's developer guide

This guide teaches the Geant4 concepts used by `geant4-python-application` and
shows how to build small simulations in Python. It is intentionally practical:
the Python package provides a high-level application, while the Geant4 kernel
does the particle transport in native C++.

It is not a complete replacement for the official Geant4 Application
Developer Guide. Use that guide for detailed physics, geometry, and toolkit
reference. Use this guide for the Python interface and this repository's
supported workflow.

## 1. The simulation idea

A Geant4 simulation normally has these pieces:

1. **Geometry**: the world, solids, logical volumes, materials, and placements.
2. **Physics**: the processes that act on particles.
3. **Primary generator**: the particles, energies, positions, and directions
   injected into the geometry.
4. **Run and event actions**: code that runs at run/event boundaries.
5. **Scoring**: the quantities extracted from steps, tracks, or volumes.

In this Python package, geometry is supplied as GDML, physics and generators
are configured through `Application`, and the built-in native actions record
events, tracks, and steps into an Awkward Array.

The normal lifecycle is:

```text
create Application -> configure -> initialize -> BeamOn/run -> analyze output
```

## 2. Installation

The package requires Python and a compatible Geant4 installation. From the
repository root:

```bash
pip install .
```

For development, install Geant4 first. The repository's README contains a
source-build example. Your Geant4 installation should include the data files
needed by the physics lists. Check the installation with:

```bash
python - <<'PY'
import geant4_python_application as g4

print("Geant4:", g4.geant4_version)
print("MT available:", g4.Application.multithreading_available())
print("Physics lists:", g4.Application.available_physics_lists()[:5])
PY
```

## 3. Your first simulation

Create `first_simulation.py`:

```python
import geant4_python_application as g4

with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
    events = app.run(10)

print(events.fields)
print("number of events:", len(events))
print(events[:2])
```

`basic_gdml` is a small air world containing a water box. The context manager
starts and stops the worker process safely. `run(10)` transports ten events.

The result is an `awkward.Array`, which is useful because each event can have a
different number of tracks, steps, and primary particles.

## 4. Choosing the physics list

A physics list selects the electromagnetic, decay, hadronic, optical, and
other processes used during transport:

```python
import geant4_python_application as g4

print(g4.Application.available_physics_lists())

with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT") as app:
    events = app.run(100)
```

`custom` is the package's built-in list. Reference lists such as `FTFP_BERT`
come from Geant4. Do not compare results from different lists as though they
were the same physical model.

Optional constructors can be added before initialization:

```python
with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT") as app:
    app.add_physics("G4EmDNAPhysics_option2")
    events = app.run(100)
```

## 5. Primary particles

The convenient generator API configures a particle gun or GPS source:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.generator.use_gps().particle("gamma").energy(2, "MeV")
    app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
    events = app.run(1000)
```

The command interface exposes ordinary Geant4 UI commands:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.commands([
        "/gun/particle e-",
        "/gun/energy 10 MeV",
        "/gun/position 0 0 -10 cm",
        "/gun/direction 0 0 1",
    ])
    events = app.run(100)
```

For advanced GPS distributions, use `/gps/...` commands through
`app.generator.commands(...)`.

## 6. Geometry with GDML

This package does not expose arbitrary Python subclasses of
`G4VUserDetectorConstruction`. Instead, provide a GDML string or file. A
minimal GDML detector has:

- `<define>` constants
- `<materials>` or references to Geant4 NIST materials
- `<solids>`
- `<structure>` containing logical volumes and physical placements
- a `<setup>` that identifies the world volume

The built-in example uses NIST materials:

```xml
<materialref ref="G4_WATER"/>
```

Run your own GDML file like this:

```python
from pathlib import Path
import geant4_python_application as g4

gdml = Path("detector.gdml").read_text()

with g4.Application(gdml=gdml) as app:
    print(app.detector.logical_volumes)
    print(app.detector.physical_volumes)
    events = app.run(100)
```

Inspect geometry before running:

```python
with g4.Application(gdml=gdml) as app:
    print(app.detector.materials)
    print(app.detector.logical_volumes)
    print(app.detector.physical_volumes)
    app.detector.check_overlaps()
```

The exact names used for scoring and sensitive volumes are the GDML physical
or logical names, so inspect them rather than guessing.

## 7. Fields and sensitive volumes

Uniform global fields can be assigned before the run:

```python
with g4.Application(gdml=gdml) as app:
    app.detector.magnetic_field = (0.0, 0.0, 1.5)  # tesla
    app.detector.electric_field = (0.0, 0.0, 0.5)  # kV/cm
    events = app.run(100)
```

To focus on a detector volume's steps:

```python
with g4.Application(gdml=gdml) as app:
    app.detector.sensitive_volumes = {"gasVolume"}
    events = app.run(100)
```

This does not create a custom Python `ProcessHits` implementation. The package
records native Geant4 steps and provides Python-side filtering and scoring.

## 8. Understanding the event output

Common fields include event IDs, primary information, tracks, and steps:

```python
print(events.fields)
print(events.id)
print(events.track.fields)
print(events.track.step.fields)
```

Because this is a jagged structure, use Awkward operations rather than assuming
every event has the same number of tracks:

```python
import awkward as ak

track_counts = ak.num(events.track.id, axis=1)
print(track_counts)
```

The default event fields can be reduced for smaller output with:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.set_event_fields({"run", "id", "track_id", "step_energy", "step_volume"})
    events = app.run(100)
```

## 9. Scoring energy deposition

Post-run scoring is often the easiest way to start:

```python
import awkward as ak
import geant4_python_application as g4

with g4.Application(gdml=g4.basic_gdml) as app:
    app.command("/gun/particle e-")
    app.command("/gun/energy 10 MeV")
    events = app.run(100)

edep = g4.Scoring.energy_deposit(events)
print("energy per event in keV:", ak.to_numpy(edep))

edep_box = g4.Scoring.energy_deposit(events, volume="box")
mesh, edges = g4.Scoring.energy_mesh(events, bins=(20, 20, 20))
```

For native Geant4 scoring meshes:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    mesh = g4.NativeScoringMesh(app, name="dose")
    mesh.box(half_size=(250, 250, 250), bins=(20, 20, 20), unit="mm")
    app.run(1000)
    mesh.dump("dose.out")
```

## 10. Saving results

```python
from pathlib import Path
from geant4_python_application import io

io.events_to_parquet(events, Path("events.parquet"))
```

ROOT output is available when `uproot` is installed:

```python
io.events_to_root(events, "events.root")
```

## 11. Visualization

Visualization requires installing/building the package with Qt/OpenGL support:

```bash
pip install . -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON
```

Then:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.command("/gun/particle gamma")
    app.command("/gun/energy 1 MeV")
    app.visualize()
```

Visualization is for inspecting geometry and tracks; production runs should
usually be performed in batch mode without the viewer.

## 12. Multithreading and MPI

Use native Geant4 CPU multithreading when the linked Geant4 was built with
multithreading:

```python
with g4.Application(gdml=g4.basic_gdml, n_threads=8) as app:
    events = app.run(100000)
```

Check availability with:

```python
print(g4.Application.multithreading_available())
```

For MPI, launch multiple Python processes and split the event count by rank:

```python
from geant4_python_application import distributed as dist

rank, size = dist.get_rank_size()
_, count = dist.split_count(100000, rank, size)

with g4.Application(gdml=g4.basic_gdml, seed=1000 + rank) as app:
    events = app.run(count)
    g4.io.events_to_parquet(events, f"events_rank_{rank}.parquet")
```

Run it with:

```bash
mpiexec -n 4 python mpi_run.py
```

MPI splitting and file merging are intentionally left to the application. Use
unique seeds and unique output files for each rank.

## 13. Reproducibility and validation

Set a seed for repeatable runs:

```python
with g4.Application(gdml=g4.basic_gdml, seed=1234) as app:
    events = app.run(1000)
```

Results can still vary with different Geant4 versions, physics lists,
thread counts, platforms, and random-engine behavior. Validate a simulation by
checking geometry overlaps, inspecting particle/energy distributions, and
running enough events for the statistical uncertainty to be meaningful.

## 14. What this interface does not currently expose

The current package is a high-level Python application rather than a complete
Python binding for every Geant4 class. It does not currently provide arbitrary
Python subclasses of detector construction, sensitive detectors, physics
processes, fields, or action classes. It also does not provide CUDA/GPU
transport. For those use cases, use native C++ Geant4 or a lower-level binding
such as `geant4_pybind`.

## 15. A recommended learning path

Work through these stages in order:

1. Run `basic_gdml` with ten events.
2. Change the particle, energy, position, and direction.
3. Inspect `events.fields`, tracks, and steps.
4. Score energy deposition in a named volume.
5. Edit or generate a GDML detector.
6. Add fields and optical physics.
7. Save results to Parquet and analyze them with NumPy/Awkward.
8. Increase event counts and enable Geant4 multithreading.
9. Use MPI splitting for independent distributed jobs.

The repository's numbered examples in `examples/geant4-examples/` correspond to
these topics and are useful as runnable companion exercises.

# Part II - Building a complete application

## 16. The application state machine

The Python `Application` is a thin controller around a native Geant4
application. It starts a child process, sends configuration calls to the
native application, and returns data to the parent Python process. This design
keeps the Geant4 kernel isolated and means that configuration must happen in
the order expected by Geant4.

The useful states are:

| State | What you can do |
| --- | --- |
| Created | Set Python constructor options such as GDML, physics, seed, and thread count. |
| Started | Configure the manager, physics, detector, and generator. |
| Initialized | Inspect the initialized detector and run events. |
| Running | Geant4 transports events and records native actions. |
| Finished | Analyze or persist the returned Awkward Array in Python. |

Most configuration must occur before the first call to `run`. For example,
physics constructors cannot be added after initialization:

```python
with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT") as app:
    app.add_physics("G4EmExtraPhysics")
    app.detector.sensitive_volumes = {"box"}
    app.initialize()
    events = app.run(100)
```

Calling `run` automatically initializes a correctly configured application, so
explicit `initialize()` is optional unless you want to validate setup first.

## 17. A complete reproducible example

The following example is a good template for new projects:

```python
from pathlib import Path

import awkward as ak
import geant4_python_application as g4


def main():
    output = Path("events.parquet")

    with g4.Application(
        gdml=g4.basic_gdml,
        physics="FTFP_BERT",
        seed=2025,
        n_threads=4,
    ) as app:
        app.set_event_fields({
            "run", "id", "track_id", "track_particle",
            "step_energy", "step_volume", "step_position",
        })
        app.generator.particle("gamma").energy(2, "MeV")
        app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
        app.detector.sensitive_volumes = {"box"}
        events = app.run(10_000)

    deposited = g4.Scoring.energy_deposit(events, volume="box")
    print("events:", len(events))
    print("mean deposited energy [keV]:", float(ak.mean(deposited)))
    g4.io.events_to_parquet(events, output)


if __name__ == "__main__":
    main()
```

Keep the simulation and analysis stages conceptually separate. The simulation
should produce a stable event record; analysis should be rerunnable without
transporting particles again.

## 18. Units, coordinates, and naming

Geant4 is unit-aware internally. In this interface, generator and field helper
methods take explicit unit strings, while GDML also declares units on numeric
values. Never silently mix millimetres, centimetres, metres, or tesla.

```python
app.generator.position(0, 0, -10, "cm")
app.generator.energy(5, "MeV")
app.detector.magnetic_field = (0, 0, 1.0)  # tesla
```

Positions in the event output and Python scoring mesh are expressed in
millimetres, and deposited energies are expressed in keV. Volume names are
case-sensitive strings originating in GDML.

A useful naming convention is:

```text
World                 world physical volume
detectorVolume        logical volume
detector              physical placement
```

Use unique, descriptive names. A name that is convenient in a GDML file is also
the name you will use later for filtering, scoring, and diagnostics.

## 19. Geometry design with GDML

### 19.1 The geometry hierarchy

The hierarchy is:

```text
solid -> logical volume -> physical volume -> world
```

A solid describes shape and dimensions. A logical volume combines a solid and
a material. A physical volume places a logical volume inside its mother. The
world is the top-level physical geometry used by the setup.

### 19.2 A small custom detector

Save this as `detector.gdml` and pass its text to the application:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gdml>
  <define>
    <constant name="worldHalf" value="500"/>
    <constant name="targetHalf" value="50"/>
  </define>
  <solids>
    <box name="worldSolid" x="worldHalf" y="worldHalf" z="worldHalf" lunit="mm"/>
    <box name="targetSolid" x="targetHalf" y="targetHalf" z="targetHalf" lunit="mm"/>
  </solids>
  <structure>
    <volume name="targetVolume">
      <materialref ref="G4_Si"/>
      <solidref ref="targetSolid"/>
    </volume>
    <volume name="worldVolume">
      <materialref ref="G4_AIR"/>
      <solidref ref="worldSolid"/>
      <physvol name="target">
        <volumeref ref="targetVolume"/>
        <position name="targetPosition" unit="mm" x="0" y="0" z="0"/>
      </physvol>
    </volume>
  </structure>
  <setup name="Default" version="1.0">
    <world ref="worldVolume"/>
  </setup>
</gdml>
```

Then validate and run:

```python
from pathlib import Path
import geant4_python_application as g4

gdml = Path("detector.gdml").read_text()
with g4.Application(gdml=gdml) as app:
    print(app.detector.materials)
    print(app.detector.physical_volumes)
    app.detector.check_overlaps()
    events = app.run(100)
```

### 19.3 Overlaps and navigation errors

Overlapping daughter volumes can cause physically incorrect navigation. Check
overlaps after loading a detector and before large production runs. If a track
behaves unexpectedly, inspect the volume names, placement coordinates, mother
volume, and units first.

## 20. Materials and optical properties

The repository's GDML examples use Geant4 NIST material names such as
`G4_AIR`, `G4_WATER`, and `G4_Si`. This is the simplest way to begin. For a
custom material, define its density and composition in GDML according to the
Geant4 GDML schema.

Optical transport needs both optical physics and optical material properties.
For example, a material that should transmit photons needs a refractive index
table. Merely setting `optical=True` does not invent optical properties:

```python
from geant4_python_application import optical as gopt

with g4.Application(gdml=gopt.optical_water_gdml, optical=True) as app:
    app.commands(gopt.scintillation_commands(yield_factor=1.0))
    events = app.run(1_000)
```

Inspect the output particle field to distinguish optical photons from the
primary particle and other secondaries.

## 21. Particle sources in detail

### 21.1 Particle-gun workflow

Use a particle gun when every event has a simple, controlled primary:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.generator.particle("proton")
    app.generator.energy(100, "MeV")
    app.generator.position(0, 0, -20, "cm")
    app.generator.direction(0, 0, 1)
    events = app.run(100)
```

### 21.2 General Particle Source

Use GPS commands for distributions in position, angle, or energy:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    app.generator.use_gps()
    app.generator.commands([
        "/gps/particle gamma",
        "/gps/ene/type Mono",
        "/gps/ene/mono 1 MeV",
        "/gps/pos/type Point",
        "/gps/pos/centre 0 0 -10 cm",
        "/gps/direction 0 0 1",
    ])
    events = app.run(100)
```

### 21.3 Event-by-event primary arrays

For a predefined beam, provide an Awkward Array containing primary fields. This
is useful when the source comes from a file or another simulation:

```python
import awkward as ak

primaries = ak.Array({
    "particle": ["gamma", "gamma", "e-"],
    "energy": [1.0, 2.0, 5.0],
    "position": {"x": [0, 0, 0], "y": [0, 0, 0], "z": [-10, -10, -10]},
    "direction": {"x": [0, 0, 0], "y": [0, 0, 0], "z": [1, 1, 1]},
})

with g4.Application(gdml=g4.basic_gdml) as app:
    events = app.run(primaries)
```

Test array-driven primaries in serial mode first. The repository currently
documents limitations for this input path in multithreaded runs.

## 22. Physics choices and statistical thinking

A simulation result is determined by geometry, materials, source, physics list,
production cuts, random seed, and event count. Changing any of these changes
the result or its interpretation.

Use a small run for functional validation, then a larger run for physics:

```python
for n_events in (1, 10, 1_000, 100_000):
    with g4.Application(gdml=g4.basic_gdml, seed=100 + n_events) as app:
        events = app.run(n_events)
    print(n_events, len(events))
```

Do not interpret a single Monte Carlo event as a measurement. Report the sample
size and an uncertainty or confidence interval for the quantity of interest.

## 23. Tracking, steps, and secondaries

An event contains primary vertices and can contain many tracks. A track is
advanced through a sequence of steps. A step can end because of geometry, a
physics interaction, a field integration limit, or another tracking condition.

Useful questions to ask in analysis are:

```python
print(events.track.particle)
print(events.track.creator_process)
print(events.track.step.volume)
print(events.track.step.process)
```

For example, select positive-energy steps and inspect their volumes:

```python
hits = events.hits()
detector_hits = hits[hits.volume == "box"]
```

The exact Awkward slicing expression can depend on the nesting shape, so begin
with `events.fields`, `events.track.fields`, and `events.track.step.fields`.

## 24. Actions and callbacks in this package

Native C++ actions are installed by the package and record run, event, track,
and step data. Python callbacks are an offline analysis layer:

```python
def on_event(event):
    print("event", event.id)


with g4.Application(gdml=g4.basic_gdml) as app:
    events = app.run_with_callbacks(10, on_event=on_event)
```

Callbacks do not replace native Geant4 `G4UserRunAction`, `G4UserEventAction`,
or `G4VSensitiveDetector` subclasses. They execute after transport over the
returned records. This makes them convenient for Python analysis, but not
suitable for changing transport behavior during a step.

## 25. Control commands and diagnostics

Any command accepted by the configured Geant4 application can be sent through
`app.command` or `app.commands`:

```python
with g4.Application(gdml=g4.basic_gdml) as app:
    print(app.list_commands("/run"))
    app.command("/run/verbose 1")
    events = app.run(1)
```

Use verbose output sparingly. Large verbose logs can dominate runtime and make
it harder to see the actual error. Prefer small event counts while debugging.

## 26. Visualization as a debugging tool

The Qt viewer is most useful for answering geometry questions: is the world
present, is the target where expected, and does the primary start in the world?
Build with visualization enabled, then run a few events. Keep visualization
separate from production output and do not use it to estimate physics results.

## 27. Production run design

For a production campaign:

1. Freeze the GDML, physics list, package version, and Geant4 version.
2. Validate the geometry and source with a one-event visualization run.
3. Run a small serial reference sample.
4. Compare a multithreaded sample with the same configuration.
5. Split large jobs into deterministic MPI ranks with unique seeds.
6. Write one output file per rank.
7. Merge and analyze outside the transport process.

Do not write all ranks to the same file unless the output format and writer are
explicitly designed for concurrent access.

# Part III - Advanced topics and boundaries

## 28. Multithreading in detail

`n_threads=0` selects the serial Geant4 run manager. A positive value selects
the multithreaded run manager and requests that many worker threads:

```python
with g4.Application(gdml=g4.basic_gdml, n_threads=8) as app:
    events = app.run(100_000)
```

The linked Geant4 library must have been compiled with multithreading. More
threads are not always faster: geometry initialization, memory pressure,
output construction, and CPU oversubscription can reduce the gain.

Benchmark with the same event count and seed policy. Validate event counts and
aggregate quantities, but do not require event ordering to be identical across
thread counts.

## 29. MPI and hybrid execution

MPI creates independent Python/Geant4 processes. Each rank should construct its
own application and run only its assigned events. A common hybrid strategy is
one MPI rank per node with several Geant4 worker threads per rank:

```python
rank, size = dist.get_rank_size()
_, count = dist.split_count(1_000_000, rank, size)

with g4.Application(
    gdml=g4.basic_gdml,
    n_threads=8,
    seed=10_000 + rank,
) as app:
    events = app.run(count)
    g4.io.events_to_parquet(events, f"events_{rank:04d}.parquet")
```

This package provides rank discovery and event splitting, not an automatic
Geant4 MPI manager, collective reduction, or file merger.

## 30. Performance and memory

Recording every step for every track can produce large nested arrays. For large
runs:

- request only the event fields needed for analysis;
- run in batches and write one file per batch;
- avoid Python callbacks for every step unless necessary;
- use native scoring meshes when a full step record is not needed;
- benchmark thread counts on the target machine.

The `Application` worker process also means that event data is transferred back
to the parent Python process. Treat that transfer as part of the cost of a
high-volume run.

## 31. Testing a simulation

A useful test suite has three layers:

### Configuration tests

Check that the GDML loads, expected volumes exist, overlaps are absent, and the
selected physics list is available.

### Transport smoke tests

Run one to ten events and assert that the result contains the expected fields
and event count.

### Physics regression tests

Run a fixed seed and compare distributions or aggregate values with tolerances.
Avoid exact event-by-event comparisons when changing thread count or platform.

```python
def test_smoke():
    with g4.Application(gdml=g4.basic_gdml, seed=7) as app:
        events = app.run(5)
    assert len(events) == 5
    assert "id" in events.fields
```

## 32. Common failure modes

**The application says the data files are missing.** Install the Geant4 datasets
and verify the environment used by Python is the same environment used to
install Geant4.

**`n_threads` fails.** Check `g4.Application.multithreading_available()` and
use `n_threads=0` with a serial Geant4 build.

**A volume cannot be found.** Print `app.detector.logical_volumes` and
`app.detector.physical_volumes`; GDML names are case-sensitive.

**Energy deposition is empty.** Confirm that step fields were requested, that
the particle enters the volume, and that the volume filter uses the actual
physical volume name.

**The detector overlaps.** Check half-length versus full-length conventions,
mother volume dimensions, placement coordinates, and units.

**The run is unexpectedly slow.** Reduce fields, disable verbose output, use a
smaller diagnostic run, and benchmark thread counts. Optical photon tracking
can be substantially more expensive than the primary transport.

## 33. Mapping native Geant4 concepts to this Python interface

| Native Geant4 concept | Python-interface equivalent |
| --- | --- |
| `G4RunManager` | `Application` and its native manager setup |
| `G4VUserDetectorConstruction` | GDML supplied to `Application` |
| `G4VUserPhysicsList` | `physics="..."` and curated `add_physics(...)` |
| `G4VUserPrimaryGeneratorAction` | `app.generator` or `/gun` and `/gps` commands |
| `G4RunManager::BeamOn` | `app.run(n_events)` |
| `G4UserRunAction` / event / track / step actions | Built-in native recording plus offline Python callbacks |
| Sensitive detector / hits | Recorded steps, `events.hits()`, and Python scoring |
| Command-based scoring | `NativeScoringMesh` |
| Geant4 visualization manager | `app.visualize()` with Qt/OpenGL build support |
| Geant4 MT run manager | `n_threads=N` |
| MPI job splitting | `distributed.get_rank_size()` and `split_count()` |

## 34. Scope boundary

This guide is deliberately detailed about the supported interface, but the
interface is not a one-to-one Python binding of the entire Geant4 class library.
If your project requires custom C++ user actions, arbitrary physics processes,
custom field equations, native digitizers, parallel worlds, advanced biasing,
or CUDA transport, you will need native Geant4 C++ or a lower-level binding.

That boundary is useful: use this package when a GDML detector, configured
physics list, standard generator, native transport, and Python analysis are a
good fit. Move to native C++ when transport-time customization is central to
the experiment.

## 35. Suggested projects

After completing the examples, build these projects in order:

1. A monoenergetic gamma beam through the water box, measuring deposited energy.
2. A silicon target with an electron beam and a magnetic field.
3. An optical scintillator with a refractive-index table and optical-photon
   count.
4. A GDML detector imported from a CAD/STL workflow.
5. A multithreaded dose map with Parquet output.
6. An MPI campaign that writes one result file per rank and performs a separate
   merge and uncertainty analysis.

For each project, write down the geometry, material, source, physics list,
field, scoring definition, event count, seed policy, and validation checks.

# Part IV - A thesis-style learning curriculum

## 36. How to read this book

This book is organized as a progression rather than a catalogue of APIs. Read
the first five chapters in order. After that, choose a project and return to
the relevant chapters while implementing it. Every serious simulation should
be understandable in four layers:

1. **Physical question** - what quantity are you trying to estimate?
2. **Monte Carlo model** - what particles, materials, processes, and geometry
   represent that question?
3. **Software implementation** - which GDML, Python configuration, and scoring
   code implement the model?
4. **Evidence** - what checks show that the result is correct and precise?

Do not begin by copying a large detector. Begin with a small experiment for
which you can predict the direction of the answer. A simulation becomes useful
when it is falsifiable: you should know what result would convince you that
the geometry, physics, or source is wrong.

## 37. Monte Carlo foundations

Geant4 transports individual particles through matter. A run with `N` primary
events is a random sample from a physical model. If `X_i` is the scored value
from event `i`, the sample mean is:

```text
mean(X) = (X_1 + X_2 + ... + X_N) / N
```

For independent events, the standard error of the mean decreases approximately
as `1 / sqrt(N)`. Doubling the precision therefore requires roughly four times
as many events. This is why a visually impressive one-event display is not a
measurement.

For a quantity with sample variance `s^2`, estimate the standard error as:

```text
standard_error = s / sqrt(N)
```

In Python:

```python
import numpy as np

values = ak.to_numpy(g4.Scoring.energy_deposit(events))
mean = values.mean()
error = values.std(ddof=1) / np.sqrt(len(values))
print(f"{mean:.4g} +/- {error:.3g} keV")
```

This statistical error does not include systematic uncertainty from geometry,
material data, physics-list choice, calibration, or an incorrect source model.

## 38. The first laboratory: a beam and a target

### Objective

Build a controlled experiment in which a monoenergetic electron crosses a water
target. Record the steps and estimate deposited energy per event.

### Procedure

```python
from pathlib import Path

import awkward as ak
import numpy as np
import geant4_python_application as g4


def run_experiment(n_events=1000):
    with g4.Application(gdml=g4.basic_gdml, seed=42) as app:
        app.set_event_fields({
            "run", "id", "track_particle", "track_id",
            "step_energy", "step_volume", "step_position",
        })
        app.commands([
            "/gun/particle e-",
            "/gun/energy 1 MeV",
            "/gun/position 0 0 -300 mm",
            "/gun/direction 0 0 1",
        ])
        return app.run(n_events)


events = run_experiment()
edep = ak.to_numpy(g4.Scoring.energy_deposit(events, volume="box"))
print("N =", len(edep))
print("mean [keV] =", np.mean(edep))
print("standard deviation [keV] =", np.std(edep, ddof=1))
```

### Interpretation

The result is not just a number. Record the particle, energy, target material,
target dimensions, physics list, seed, event count, and volume name alongside
it. A result without configuration metadata cannot be reproduced.

### Exercises

1. Change the electron energy from 1 MeV to 10 MeV.
2. Replace the electron with a gamma ray and explain the changed distribution.
3. Move the source outside the world and observe the diagnostic behavior.
4. Set the target volume as sensitive and compare the resulting step records.

## 39. Designing a detector model

### 39.1 Start with the question

If the question is “how much energy reaches the sensor?”, the geometry needs a
sensor volume and a scoring definition. If the question is “what is the track
length in gas?”, the geometry needs the gas volume and the analysis must sum
step lengths or use an appropriate recorded field. Geometry should be driven by
the observable, not by visual complexity.

### 39.2 World volume

The world must contain every possible particle position and secondary track.
Make it large enough that particles do not begin outside it, but do not make it
unnecessarily enormous when using detailed navigation. Use a simple material
such as air or vacuum unless the physical question requires something else.

### 39.3 Detector volume

Give each important detector component a unique physical name. Put the material
on the logical volume and the position on the physical placement. This lets you
reuse a logical volume and place it several times while retaining distinct
physical names for analysis.

### 39.4 Geometry validation checklist

Before physics validation, check:

- world dimensions contain the source and expected secondaries;
- all solids have the intended full lengths and half lengths;
- daughter placements are inside their mothers;
- rotations use the intended convention;
- material names resolve;
- repeated placements have unique analysis names;
- overlap checks pass;
- a one-event visualization looks correct.

## 40. Materials as physical models

Material density affects stopping power and interaction probability. Elemental
composition affects cross sections and secondary production. Optical properties
affect refraction, reflection, absorption, and photon yield. A material name is
therefore not merely a label.

For each custom material, document:

- density and temperature;
- elemental or component composition;
- state and pressure where relevant;
- optical property tables and their energy/wavelength domain;
- the source of the values;
- the version of the data used.

Do not extrapolate optical tables silently beyond their defined domain. If a
simulation depends on a material parameter, include a validation plot or a
small numerical check in the project repository.

## 41. Selecting a physics list responsibly

A reference physics list is a coherent collection of models and processes. It
is usually safer than assembling individual processes without understanding
their interactions. Select a list based on particle types, energy range,
target materials, and required precision.

Use this decision process:

1. Identify all primary and likely secondary particle species.
2. Identify the lowest and highest relevant energies.
3. Identify whether electromagnetic, hadronic, decay, optical, or DNA physics
   is required.
4. Choose a documented reference list that covers the domain.
5. Run a small sensitivity comparison against another plausible list.
6. Record the choice and rationale.

Adding a constructor such as `G4EmDNAPhysics_option2` is an expert operation.
Confirm that the geometry, energy range, chemistry assumptions, and output
interpretation are appropriate before using it for a scientific conclusion.

## 42. Source modelling and phase space

The primary source is often the largest systematic uncertainty. Specify:

- particle species and charge;
- energy distribution;
- position distribution;
- direction and angular distribution;
- event time if relevant;
- correlations among primaries;
- normalization and exposure.

A source file may contain correlated variables. Preserve those correlations when
turning it into an Awkward Array. Do not independently shuffle energy and
direction unless the physical source is truly uncorrelated.

For multiple primaries per event, preserve the event boundaries. One event with
ten correlated primary vertices is not equivalent to ten independent events.

## 43. Data model and analysis architecture

The event output has a nested structure because physics is nested:

```text
run
  event
    primary vertices
    tracks
      steps
```

Use the event as the unit of statistical analysis. If you flatten all steps and
compute a mean without event weights, events with many steps receive more
influence than events with few steps. Decide whether you need an event-level,
track-level, or step-level observable before flattening.

### Event-level example

```python
edep_per_event = g4.Scoring.energy_deposit(events)
mean_edep = ak.mean(edep_per_event)
```

### Step-level example

```python
hits = events.hits(volume="box")
positive_steps = ak.flatten(hits.energy, axis=None)
```

These answer different questions. State the choice in the analysis document.

## 44. Scoring design patterns

### 44.1 Recorded-step scoring

Use recorded steps when you need positions, processes, track IDs, or custom
Python analysis. This is flexible but can consume substantial memory.

### 44.2 Native mesh scoring

Use `NativeScoringMesh` when you need a spatial energy-deposition map and do not
need every track and step in Python. This delegates scoring to native Geant4.

### 44.3 Hybrid scoring

Use a small diagnostic run with full steps, then a large production run with
minimal fields or a native mesh. This gives both interpretability and scale.

### 44.4 Efficiency and normalization

If you simulate only a biased or filtered sample, the result needs the correct
weighting. The present high-level package does not expose every Geant4 biasing
class, so treat event filtering as an analysis selection, not as an unbiased
estimate of the original flux.

## 45. Validation as a scientific workflow

Validation has three distinct meanings:

1. **Software validation**: does the program run and produce structurally valid
   output?
2. **Physics verification**: does the implementation reproduce a known result
   or limiting case?
3. **Experimental validation**: does the simulation agree with measured data
   within the combined uncertainty?

For every new detector, create a validation table:

| Test | Expected behavior | Result | Status |
| --- | --- | --- | --- |
| Geometry load | All named volumes exist | ... | pass/fail |
| Overlap check | No overlaps in target region | ... | pass/fail |
| Empty field | Straight neutral-particle path | ... | pass/fail |
| Energy conservation | Balance within tolerance | ... | pass/fail |
| Physics comparison | Agreement with reference | ... | pass/fail |
| Thread comparison | Aggregate agreement | ... | pass/fail |

Keep failed tests visible. A simulation project becomes trustworthy when its
failures are discoverable rather than hidden.

## 46. Uncertainty studies

Vary one assumption at a time and compare the resulting distributions:

- physics list;
- material density or composition;
- detector dimensions;
- source energy or angular spread;
- field strength;
- production settings;
- event count;
- thread count and rank count.

Use independent seeds for independent systematic scenarios. Use a common-random-
number strategy only when you understand the covariance benefit and can explain
it in the analysis.

## 47. A capstone project: a small dose study

### Research question

Estimate the energy deposited in a water target by a monoenergetic gamma beam,
compare two photon energies, and report a statistical uncertainty.

### Project structure

```text
dose-study/
  detector.gdml
  run.py
  analyze.py
  results/
  README.md
```

### Run script

```python
from pathlib import Path
import geant4_python_application as g4


def run_energy(energy_mev, n_events, seed):
    gdml = Path("detector.gdml").read_text()
    with g4.Application(gdml=gdml, physics="FTFP_BERT", seed=seed) as app:
        app.set_event_fields({"id", "step_energy", "step_volume"})
        app.commands([
            "/gun/particle gamma",
            f"/gun/energy {energy_mev} MeV",
            "/gun/position 0 0 -300 mm",
            "/gun/direction 0 0 1",
        ])
        events = app.run(n_events)
    g4.io.events_to_parquet(events, f"results/events_{energy_mev}MeV.parquet")
    return g4.Scoring.energy_deposit(events, volume="target")


if __name__ == "__main__":
    for energy in (1, 5):
        run_energy(energy, n_events=100_000, seed=1000 + energy)
```

### Analysis questions

1. Does the mean deposited energy increase monotonically with beam energy?
2. How does the fraction of zero-deposition events change?
3. Is the difference larger than the combined statistical uncertainty?
4. Does changing from serial to four threads change the aggregate result?
5. What detector or source assumptions dominate the difference?

The capstone is complete only when the answer includes configuration metadata,
plots or tables, uncertainties, and a statement of limitations.

## 48. From Python to native Geant4

Eventually you may need a feature outside this package's binding boundary. The
conceptual translation remains useful:

- Python GDML configuration corresponds to native detector construction.
- `app.run` corresponds to `BeamOn`.
- Python scoring corresponds to native run/event/step actions or scorers.
- Offline callbacks correspond to analysis after an event record exists.
- A reference physics-list name corresponds to native physics-list factory use.

When moving to C++, first reproduce the Python result with the same geometry,
source, physics list, seed policy, and event count. Then introduce the native
customization one feature at a time. This makes it possible to distinguish a
binding difference from a physics-model difference.

## 49. Final competence checklist

A reader is ready to use this package independently when they can:

- explain the run, event, track, and step hierarchy;
- create and validate a GDML detector;
- choose and justify a physics list;
- define a reproducible source;
- configure fields and optical transport where supported;
- choose an event-level or step-level observable;
- produce an uncertainty estimate;
- save and reload results;
- compare serial, multithreaded, and MPI runs;
- diagnose geometry, data, and source failures;
- state which features require native Geant4;
- document a simulation so another person can reproduce it.

That is the difference between making a Geant4 script run and conducting a
defensible Monte Carlo study.

# Part V - How to write a Geant4 Python program

## 50. The anatomy of a simulation program

A maintainable simulation program usually contains five layers:

```text
configuration -> detector/source setup -> transport -> scoring -> analysis
```

Keep these layers visible in the code. A useful first file is:

```text
my_simulation/
  run_simulation.py     # creates the application and runs events
  analyze_results.py     # reads output and computes physics quantities
  detector.gdml         # geometry and material references
  results/               # generated output, not source code
```

Do not put a 500,000-event run at module import time. Put execution inside
`main()` and protect it with `if __name__ == "__main__":`. This is important
when launching multiple processes with MPI and makes the file importable from
tests or notebooks.

## 51. Write the smallest runnable program

Start by writing this exact skeleton:

```python
import geant4_python_application as g4


def main():
    with g4.Application(gdml=g4.basic_gdml, seed=1234) as app:
        events = app.run(10)
    print("events:", len(events))


if __name__ == "__main__":
    main()
```

Line by line:

- `import ... as g4` loads the public Python interface.
- `main()` gives the program a clear entry point.
- `Application(...)` creates the simulation controller.
- `gdml=...` supplies the detector description.
- `seed=1234` makes the random sequence reproducible for this configuration.
- `with` starts the native application and stops it even if an exception occurs.
- `app.run(10)` transports ten primary events.
- `events` is a nested `awkward.Array`, not a normal list of Python objects.
- The `__main__` guard prevents accidental execution during import.

Run it from the project directory:

```bash
python run_simulation.py
```

If this fails, do not add physics complexity yet. First fix installation,
dataset, and environment problems with this smallest program.

## 52. Add one feature at a time

The safest way to write a simulation is incremental:

```python
def main():
    with g4.Application(gdml=g4.basic_gdml, seed=1234) as app:
        # 1. Configure the source.
        app.generator.use_gun()
        app.generator.particle("gamma")
        app.generator.energy(1, "MeV")
        app.generator.position(0, 0, -30, "cm")
        app.generator.direction(0, 0, 1)

        # 2. Run a tiny smoke test.
        events = app.run(1)

    print(events)
```

Run one event, inspect it, and only then increase the event count. This creates
a short feedback loop for source and geometry mistakes.

## 53. Write a reusable configuration function

Once the first script works, move configuration into named functions:

```python
import geant4_python_application as g4


def configure_source(app, particle="gamma", energy_mev=1.0):
    app.generator.use_gun()
    app.generator.particle(particle)
    app.generator.energy(energy_mev, "MeV")
    app.generator.position(0, 0, -30, "cm")
    app.generator.direction(0, 0, 1)


def configure_detector(app):
    app.detector.sensitive_volumes = {"box"}
    app.detector.check_overlaps()


def run_simulation(n_events, seed=1234):
    with g4.Application(
        gdml=g4.basic_gdml,
        physics="FTFP_BERT",
        seed=seed,
    ) as app:
        configure_source(app)
        configure_detector(app)
        return app.run(n_events)


def main():
    events = run_simulation(100)
    print("generated", len(events), "events")


if __name__ == "__main__":
    main()
```

The important design choice is that `configure_source` receives an existing
application. It does not create a second application. Geant4 permits only one
kernel/application instance in the worker process.

## 54. Write a real command-line program

For research work, hard-coded values should become command-line options:

```python
import argparse
from pathlib import Path

import geant4_python_application as g4


def parse_args():
    parser = argparse.ArgumentParser(description="Run a gamma transport study")
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--energy", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--gdml", type=Path)
    parser.add_argument("--output", type=Path, default=Path("events.parquet"))
    return parser.parse_args()


def main():
    args = parse_args()
    gdml = args.gdml.read_text() if args.gdml else g4.basic_gdml

    with g4.Application(
        gdml=gdml,
        physics="FTFP_BERT",
        n_threads=args.threads,
        seed=args.seed,
    ) as app:
        app.generator.use_gun().particle("gamma").energy(args.energy, "MeV")
        app.generator.position(0, 0, -30, "cm").direction(0, 0, 1)
        events = app.run(args.events)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    g4.io.events_to_parquet(events, args.output)
    print(f"wrote {len(events)} events to {args.output}")


if __name__ == "__main__":
    main()
```

Examples:

```bash
python run_simulation.py --events 100 --energy 1
python run_simulation.py --events 100000 --energy 5 --threads 8
python run_simulation.py --gdml detector.gdml --output results/run.parquet
```

Command-line arguments turn a script into a reproducible experiment: the
command itself records the most important choices.

## 55. Write the analysis program separately

Do not rerun Geant4 just to change a plot or a summary statistic. Save the
event data and write a separate analysis program:

```python
from pathlib import Path

import awkward as ak
import numpy as np
import geant4_python_application as g4


def main():
    events = g4.io.events_from_parquet(Path("results/events.parquet"))
    edep = ak.to_numpy(g4.Scoring.energy_deposit(events, volume="box"))
    mean = float(np.mean(edep))
    error = float(np.std(edep, ddof=1) / np.sqrt(len(edep)))
    print(f"N={len(edep)}")
    print(f"mean deposited energy = {mean:.5g} +/- {error:.3g} keV")


if __name__ == "__main__":
    main()
```

This separation lets you improve the analysis without changing the simulated
sample. It also makes code review easier: transport code answers “what was
simulated?” and analysis code answers “how was it summarized?”

## 56. Write a detector as a parameterized project

For a detector that changes between studies, keep the GDML template and the
Python run code separate. Generate a GDML string from a small configuration
object, or keep several checked-in GDML files with explicit names:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DetectorConfig:
    path: Path
    target_name: str


def load_detector(config: DetectorConfig) -> str:
    text = config.path.read_text()
    if not text.strip():
        raise ValueError(f"empty GDML file: {config.path}")
    return text
```

Validate the configuration before starting a long run. Fail early when a file
is missing, a volume name is wrong, or the event count is negative.

## 57. Write tests before scaling up

Add tests that exercise the code without requiring a large physics sample:

```python
def test_source_and_event_count():
    with g4.Application(gdml=g4.basic_gdml, seed=9) as app:
        app.generator.particle("gamma").energy(1, "MeV")
        events = app.run(3)

    assert len(events) == 3
    assert "id" in events.fields
```

Add a geometry test:

```python
def test_detector_names():
    with g4.Application(gdml=g4.basic_gdml) as app:
        assert "box" in app.detector.physical_volumes
        app.detector.check_overlaps()
```

Tests are not a substitute for physics validation, but they prevent ordinary
programming changes from silently breaking the experiment.

## 58. A complete writer's template

Use this template as the starting point for a serious new simulation:

```python
#!/usr/bin/env python3
"""Transport primary particles through a GDML detector and save events."""

import argparse
from pathlib import Path

import geant4_python_application as g4


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("events.parquet"))
    return parser


def configure(app):
    app.set_event_fields({
        "run", "id", "primaries", "track_particle",
        "track_creator_process", "step_energy", "step_volume",
    })
    app.generator.use_gps()
    app.generator.particle("gamma").energy(2, "MeV")
    app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
    app.detector.sensitive_volumes = {"box"}
    app.detector.check_overlaps()


def run(args):
    with g4.Application(
        gdml=g4.basic_gdml,
        physics="FTFP_BERT",
        n_threads=args.threads,
        seed=args.seed,
    ) as app:
        configure(app)
        return app.run(args.events)


def main():
    args = build_parser().parse_args()
    if args.events <= 0:
        raise SystemExit("--events must be positive")
    events = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    g4.io.events_to_parquet(events, args.output)
    print(f"saved {len(events)} events to {args.output}")


if __name__ == "__main__":
    main()
```

When adapting this template, change one section at a time and keep the
simulation executable after each change. This is how a short educational script
becomes a dependable research program.
