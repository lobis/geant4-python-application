# Geant4 Python examples

Runnable Python ports of the Geant4 11.4.2 examples that fit the current
`geant4_python_application` interface. Each entry point opens the Geant4 Qt
viewer by default; pass `--batch` to run without a window.

## Included ports

- `basic/B1/b1.py`: medical phantom with tissue and bone scoring volumes.
- `basic/B4/b4.py`: lead/liquid-argon sampling calorimeter.
- `advanced/GoldFoilExperiment/gold_foil.py`: Rutherford gold-foil scattering.
- `run_gdml.py`: a generic Qt runner for standalone GDML detector geometries.

## Running an example

```bash
conda activate geant4-python
cd ~/Desktop/Geant4-11.4.2-examples-python/basic/B1
python b1.py
```

Use the Qt command panel to execute `/run/beamOn 100`. For a non-interactive
run, add `--batch -n 1000`.

## Not yet portable

The original Geant4 example tree is retained separately in
`~/Desktop/Geant4-11.4.2-examples`. Examples requiring custom C++ user
actions, physics lists, fields, optical surfaces, MPI, VTK, DNA chemistry, or
external generators need additional bindings before they can become faithful
Python ports.
