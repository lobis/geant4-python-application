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
  [awkward array](https://github.com/scikit-hep/awkward) for further analysis

## Installation

A lot of work has been done to make the installation as easy as possible. This
package is fully pip installable and should work on all major platforms.

The package itself does not contain any Geant4 data files. These files are
needed to perform any kind of simulation. They will be downloaded to a temporary
directory automatically during simulation startup.

```bash
pip install geant4-python-application
```

### Geant4 data files

The Python wheels for this package do not contain any Geant4 data files due to
their size. These files will be downloaded on demand without the need of any
user interaction.

The default location for these files can be obtained by calling:

```bash
python -c "import geant4_python_application; print(geant4_python_application.get_data_path())"
```

**Uninstalling the package will not remove the data files. The user is
responsible for removing them manually.**

#### Overriding the default data path

The default data path can be overridden by calling `application_directory`. This
should be done before the application is initialized.

```python
from geant4_python_application import application_directory

application_directory("/some/other/path")
```

Overriding the default data directory is encouraged when submitting batch jobs
to a cluster in order to avoid downloading the data files multiple times. In
this case the application directory should point to some shared location.

#### Using a temporary directory

A temporary directory can be used by calling:

```python
from geant4_python_application import application_directory

application_directory(temp=True)
```

The operating system will take care of cleaning up the temporary directory.

It is possible that the operating system will delete only some of the files in
the temporary directory which can lead to a Geant4 runtime error. In this case
it's recommended to delete the temporary directory manually and let the
application recreate it again.

## Usage

```python
import geant4_python_application as g4

# Use a temporary directory for the Geant4 data files (remove this line to use the default location)
g4.application_directory(temp=True)

with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
    events = app.run(n_events=100)

print(events)
```
