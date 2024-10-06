# Geant4 Python Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lobis/geant4-python-application/HEAD?labpath=attenuation.ipynb)
[![Binder](https://binderhub.ssl-hep.org/badge_logo.svg)](https://binderhub.ssl-hep.org/v2/gh/lobis/geant4-python-application/HEAD?labpath=attenuation.ipynb)

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

## Installation

The package is pip installable and should work on all major platforms. Geant4 is
not required to be installed on the system as the PyPI distribution includes a
statically linked version of Geant4.

However, for the time being, it's recommended to install from the GitHub
repository to get the latest version, which makes Geant4 a necessary dependency.

The provided `Dockerfile` can be used for development purposes and as
documentation on the required dependencies. To build the image run from the root
directory:

```bash
docker build -t geant4-python-application .
```

Geant4 can be installed using conda:

```bash
conda install -c conda-forge geant4
```

For development purposes however, it's recommended to install Geant4 from source
with a similar configuration to the one used in the CI:

```bash
git clone https://github.com/Geant4/geant4.git ./geant4-source --depth 1 --branch v11.2.2

cmake -B ./geant4-build -S ./geant4-source -DCMAKE_INSTALL_PREFIX=./geant4-install -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 -DGEANT4_USE_GDML=ON -DGEANT4_INSTALL_EXAMPLES=OFF -DGEANT4_INSTALL_DATA=OFF -DGEANT4_BUILD_TLS_MODEL=global-dynamic -DBUILD_STATIC_LIBS=ON -DBUILD_SHARED_LIBS=OFF -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_C_FLAGS=-fPIC -DGEANT4_USE_SYSTEM_EXPAT=OFF
cmake --build ./geant4-build --parallel $(nproc) --config Release --target install
```

One common installation issue is the dependency `xerces-c`. You may be able to
install it from your package manager (e.g. `apt-get install libxerces-c-dev) but
it's also possible to build it from source. In this case make sure the
installation directory is accessible or just use the default system path.

```bash
git clone https://github.com/apache/xerces-c.git ./xerces-source
git -C ./xerces-source checkout tags/v3.2.5
cmake -B ./xerces-build -S ./xerces-source -DCMAKE_INSTALL_PREFIX=./xerces-install  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 -DBUILD_SHARED_LIBS=OFF -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_C_FLAGS=-fPIC -Dnetwork-accessor=socket -Dtranscoder=iconv
cmake --build ./xerces-build --parallel $(nproc) --config Release --target install
```

After all dependencies are met, you should be able to install the package by
running the following command from the root directory:

```bash
pip install .
```

### Geant4 data files

Geant4 comes with a large set of data files which are required in order to run.
The data files are the bulk of the Geant4 installation and can be quite large.
These data files are not included in the Python wheels for this package due to
its size.

The python package automatically manages the download of the data files. To
check the location of the data files, run the following command:

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

The operating system should take care of cleaning up the temporary directory.

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
