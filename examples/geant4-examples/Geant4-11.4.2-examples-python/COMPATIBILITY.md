# Compatibility with the official Geant4 examples

This directory contains Python adaptations, not mechanical translations of
the C++ sources. They exercise the same detector concept using functionality
currently exposed by `geant4_python_application`.

## Runnable adaptations

| Official family | Python entry point | Coverage |
|---|---|---|
| basic/B1 | `basic/B1/b1.py` | Geometry, beam, volume energy scoring |
| basic/B2 | `basic/B2/b2.py` | Target, tracker chambers, field, step-derived hits |
| basic/B3 | `basic/B3/b3.py` | PET geometry and crystal/patient energy scoring |
| basic/B4 | `basic/B4/b4.py` | Sampling calorimeter and layer energy scoring |
| basic/B5 | `basic/B5/b5.py` | Spectrometer geometry, field, detector energy scoring |
| GoldFoilExperiment | `advanced/GoldFoilExperiment/gold_foil.py` | Rutherford-scattering workflow and CSV output |
| NanoparticleTherapy | `advanced/NanoparticleTherapy/*.py` | Geometric/physics adaptations and dose summaries |
| extended/eventgenerator/exgps | `extended/eventgenerator/exgps/exgps.py` | Native GPS and primary-spectrum output |
| extended/eventgenerator/particleGun | `extended/eventgenerator/particleGun/particle_gun.py` | Python-sampled source modes and transport |
| extended/eventgenerator/HepMC | `extended/eventgenerator/HepMC/hepmc.py` | Minimal HepMC2 parser adapter; no native HepMC SDK |
| extended/field/field01 | `extended/field/field01/field01.py` | Uniform magnetic-field tracking study |
| extended/field/field02 | `extended/field/field02/field02.py` | Native uniform electric field and absorber scoring |
| extended/optical/OpNovice | `extended/optical/OpNovice/op_novice.py` | Native optical transport and photon counting |
| extended/optical/LXe | `extended/optical/LXe/lxe.py` | LXe scintillation/transport; post-run photon analysis replaces PMT hit callbacks |
| extended/optical/wls | `extended/optical/wls/wls.py` | Native WLS absorption/re-emission in a GDML fiber |
| extended/analysis/AnaEx01 | `extended/analysis/AnaEx01/ana_ex01.py` | Calorimeter energy analysis and CSV ntuple |
| extended/analysis/AnaEx02 | `extended/analysis/AnaEx02/ana_ex02.py` | Nested event persistence through Parquet |
| extended/analysis/AnaEx03 | `extended/analysis/AnaEx03/ana_ex03.py` | ROOT summary adapter through uproot |
| extended/electromagnetic/TestEm1 | `extended/electromagnetic/TestEm1/test_em1.py` | Electromagnetic process and energy-deposit survey |
| extended/hadronic/Hadr00 | `extended/hadronic/Hadr00/hadr00.py` | Hadronic target and secondary-particle survey |
| extended/medical/GammaTherapy | `extended/medical/GammaTherapy/gamma_therapy.py` | Simplified therapy geometry with native energy mesh |
| extended/medical/electronScattering | `extended/medical/electronScattering/electron_scattering.py` | Simplified foil-scattering benchmark |
| extended/parameterisations/Par01 | `extended/parameterisations/Par01/par01.py` | Static parameterisation expanded to GDML placements |
| extended/physicslists/factory | `extended/physicslists/factory/factory.py` | Runtime selection from native Geant4 reference lists |
| extended/radioactivedecay/rdecay01 | `extended/radioactivedecay/rdecay01/rdecay01.py` | Native radioactive decay and product survey |
| extended/runAndEvent/RE01 | `extended/runAndEvent/RE01/re01.py` | Multiple primary vertices preserved per event |

Each entry point opens Qt by default and accepts `--batch` for non-interactive
execution.

## Standalone GDML geometries

The official Desktop tree currently contains 144 `.gdml` files. A GDML file
that includes a complete `<setup>` and world volume can be tried directly:

```bash
python run_gdml.py /absolute/path/to/detector.gdml --batch -n 10
```

Many official GDML files are fragments included by a C++ detector or another
GDML file. Those fragments are not standalone examples and must not be passed
to the runner by themselves.

## Supported concepts, but not faithful class-for-class ports

- Reference physics lists and selected additional physics constructors
- Particle gun and General Particle Source commands
- Uniform global magnetic and electric fields
- Optical materials/surfaces expressed in GDML and optical physics
- Step-derived scoring, hits, and post-run Python callbacks
- Tessellated STL geometry, VTK/ROOT/Parquet export, minimal HepMC input
- Rank-aware event splitting

## Still requiring additional native bindings

- Arbitrary Python subclasses of Geant4 detector, action, process, field,
  sensitive-detector, and hit-collection C++ interfaces
- Parameterised geometry callbacks and custom equation/stepper classes
- Live callbacks during transport (current Python callbacks are post-run)
- Arbitrary `G4MultiFunctionalDetector` primitives beyond the command-based
  native energy-deposit mesh now exposed by `NativeScoringMesh`
- Full Geant4 MPI lifecycle and result merging
- DNA chemistry scheduling and chemistry-time actions
- Examples that depend on ROOT classes, VTK classes, CAD kernels, DICOM data,
  VecGeom, Pythia, or other external native SDKs

An example in the final category can only be called compatible after its
required native interface is bound and its expected physics result is tested.
