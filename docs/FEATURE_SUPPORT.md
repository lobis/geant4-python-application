# Geant4 feature support audit

This matrix distinguishes native Geant4 execution from Python adapters. A
feature is not marked supported merely because a similarly named proof script
exists.

| Capability | Status | Current implementation |
|---|---|---|
| Detector construction | Partial | Complete GDML strings/files; no Python subclass of `G4VUserDetectorConstruction` |
| Run/event/track/step actions | Partial | Native built-in C++ actions record events; user callbacks run after transport |
| Multiple primary vertices | Supported | Nested Awkward `primaries` records generate and preserve all vertices in each event |
| Sensitive detectors/hits | Partial | Logical volumes can be marked sensitive and all steps are recorded; no custom Python `ProcessHits` or native typed hit collection |
| Parameterised geometry | Partial | Expanded placements can be generated in Python/GDML; no live `G4VPVParameterisation` callback |
| Physics lists/processes | Partial | Reference lists and a curated set of `G4VPhysicsConstructor` classes; no arbitrary Python process/particle subclass |
| Fields/equations/steppers | Partial | Uniform global B and E with native Geant4 integration; no user equation/stepper binding |
| Optical materials/processes | Supported (GDML) | RINDEX, scintillation, WLS and optical surfaces execute natively; no Python PMT/SD callback |
| Repeated geometry | Adapter | Regular layouts can be expanded to ordinary GDML placements; no live parameterisation callback |
| Native scoring meshes | Supported (energy) | `NativeScoringMesh` drives `G4ScoringManager`; Python `Scoring` remains a separate post-run tool |
| MPI/distributed | Partial | `mpi4py` rank discovery and event splitting; no Geant4 MPI manager or automatic merge |
| DNA | Partial | DNA physics and chemistry constructors are selectable; chemistry scheduler/time-step actions are not exposed |
| ROOT | Adapter | `uproot` summary I/O, not Geant4 ROOT analysis classes |
| VTK | Adapter | Legacy VTK mesh export, not Geant4 VTK visualization classes |
| CAD | Adapter | ASCII STL/tessellated GDML, not STEP/IGES or a CAD kernel |
| Pythia/HepMC | Partial adapter | Minimal HepMC2 primary import; no Pythia native integration |
| DICOM/medical | Partial | GDML medical geometries and dose post-processing; no DICOM image/voxel pipeline |

## Binding work still required

Python subclassing of Geant4 virtual interfaces is complicated by the package's
worker-process architecture: arbitrary Python callables must execute safely in
the simulation process and cannot be treated as ordinary pickleable state. New
live callback APIs therefore require an explicit callback transport/lifetime
design, not only pybind11 trampoline declarations.
