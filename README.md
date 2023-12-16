# Geant4 Python Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lobis/geant4-python-application/HEAD)
[![Wheels](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml)
[![Build and Test](https://github.com/lobis/geant4-python-application/actions/workflows/build-test.yaml/badge.svg)](https://github.com/lobis/geant4-python-application/actions/workflows/test.yaml)

⚠️ This project is currently in a very early stage of development ⚠️

The goal of this project is to provide an accessible pythonic interface to do
radiation transport simulations with Geant4.

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
  [awkward array](https://github.com/scikit-hep/awkward) for further analysis

## Installation

A lot of work has been done to make the installation as easy as possible. This
package is fully pip installable and should work on all major platforms.

The package itself does not contain any Geant4 data files. These files are
needed to perform any kind of simulation. They will be downloaded to a temporary
directory automatically during simulation startup.

```bash
pip install -i https://test.pypi.org/simple/ geant4-python-application==0.0.2.dev1
```

## Usage

```python
from geant4_python_application import Application, basic_gdml

# The data files will be downloaded to a temporary directory the first time this is called
app = Application()

app.setup_manager(n_threads=4)
app.setup_physics()
app.setup_detector(gdml=basic_gdml)
app.setup_action()

app.initialize()

events = app.run(n_events=100)

print(events)
```
