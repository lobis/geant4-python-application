# Geant4 Python examples

Runnable Python ports of the Geant4 11.4.2 examples that fit the current
`geant4_python_application` interface. Each entry point opens the Geant4 Qt
viewer by default; pass `--batch` to run without a window.

## Included ports

- `basic/B1/b1.py`: medical phantom with tissue and bone scoring volumes.
- `basic/B2/b2.py`: fixed target, six tracker chambers, hits, and transverse field.
- `basic/B3/b3.py`: schematic PET ring with crystal and patient energy scoring.
- `basic/B4/b4.py`: lead/liquid-argon sampling calorimeter.
- `basic/B5/b5.py`: double-arm spectrometer adaptation with field and detector scoring.
- `advanced/GoldFoilExperiment/gold_foil.py`: Rutherford gold-foil scattering.
- `extended/eventgenerator/exgps/exgps.py`: GPS source distributions and primary analysis.
- `extended/eventgenerator/particleGun/particle_gun.py`: sampled particle-gun modes.
- `extended/eventgenerator/HepMC/hepmc.py`: minimal HepMC2 ASCII primary adapter.
- `extended/field/field02/field02.py`: constant electric-field transport.
- `extended/optical/OpNovice/op_novice.py`: optical generation and transport.
- `extended/optical/LXe/lxe.py`: liquid-xenon scintillation and optical transport.
- `extended/optical/wls/wls.py`: wavelength-shifting fiber transport.
- `extended/analysis/AnaEx01/ana_ex01.py`: sampling-calorimeter analysis output.
- `extended/analysis/AnaEx02/ana_ex02.py`: nested Parquet event output.
- `extended/analysis/AnaEx03/ana_ex03.py`: ROOT summary output via uproot.
- `extended/field/field01/field01.py`: magnetic-field tracking study.
- `extended/radioactivedecay/rdecay01/rdecay01.py`: radioactive-decay track survey.
- `extended/electromagnetic/TestEm1/test_em1.py`: EM process survey.
- `extended/medical/GammaTherapy/gamma_therapy.py`: photon-therapy phantom and native dose mesh.
- `extended/medical/electronScattering/electron_scattering.py`: foil-scattering benchmark adaptation.
- `extended/hadronic/Hadr00/hadr00.py`: hadronic target and secondary survey.
- `extended/parameterisations/Par01/par01.py`: expanded parameterised detector layout.
- `extended/physicslists/factory/factory.py`: native reference-physics-list factory selection.
- `extended/runAndEvent/RE01/re01.py`: multiple primary vertices in each event.
- `run_gdml.py`: a generic Qt runner for standalone GDML detector geometries.

## Running an example

```bash
conda activate geant4-python
cd ~/Desktop/Geant4-11.4.2-examples-python/basic/B1
python b1.py
```

Use the Qt command panel to execute `/run/beamOn 100`. For a non-interactive
run, add `--batch -n 1000`.

Validate every claimed Python port against an original Geant4 tree with:

```bash
python tools/audit_examples.py ~/Desktop/Geant4-11.4.2-examples \
  examples/geant4-examples/Geant4-11.4.2-examples-python
```

## Not yet portable

The original Geant4 example tree is retained separately in
`~/Desktop/Geant4-11.4.2-examples`. Examples requiring live custom C++ user
actions, arbitrary fields/processes, native MPI, DNA chemistry scheduling, or
external native SDKs still need additional bindings before they can become
faithful Python ports. The compatibility report distinguishes faithful native
features from Python/GDML adaptations.
