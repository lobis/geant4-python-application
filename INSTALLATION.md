# Installation

Prebuilt wheels bundle a compiled Geant4 11.2.2, so on supported platforms you
**do not need to install Geant4 (C++) yourself**. Building from source still
requires a Geant4 installation.

| Platform              | Python      | Prebuilt wheel | Qt viewer (`[gui]`) |
| --------------------- | ----------- | -------------- | ------------------- |
| macOS, Apple Silicon  | 3.8 – 3.13  | yes            | yes                 |
| macOS, Intel          | 3.8 – 3.13  | yes            | yes                 |
| Linux x86_64          | 3.8 – 3.13  | yes            | yes (needs a desktop with OpenGL) |
| Linux aarch64, Windows | —          | no             | build from source   |

## Install a prebuilt wheel

### From PyPI

> **Not published yet.** The first PyPI release will be 0.1.0. Until then,
> `pip install geant4-python-application` fails with "No matching distribution
> found"; use the [CI wheels](#from-a-ci-build-before-the-first-release)
> instead.

```bash
pip install "geant4-python-application[gui]"
```

Leave out `[gui]` for a physics-only install without Qt:

```bash
pip install geant4-python-application
```

### From a GitHub release

Each [GitHub release](https://github.com/lobis/geant4-python-application/releases)
from 0.1.0 on also has the wheels attached. pip picks the right wheel for your
platform and Python version; replace `<tag>` with the release tag (e.g.
`v0.1.0`):

```bash
pip install "geant4-python-application[gui]" \
  --find-links https://github.com/lobis/geant4-python-application/releases/expanded_assets/<tag>
```

### From a CI build (before the first release)

Every run of the
[Wheels workflow](https://github.com/lobis/geant4-python-application/actions/workflows/wheels.yaml)
keeps its wheels as downloadable artifacts for 90 days. Pick a successful run
and download the artifact for your platform: `cibw-wheels-ubuntu-latest-x86_64`
(Linux), `cibw-wheels-macos-15-arm64` (Apple Silicon) or
`cibw-wheels-macos-15-intel-x86_64` (Intel Mac). From the run page this needs a
GitHub login; with the [GitHub CLI](https://cli.github.com) (`gh auth login`
first):

```bash
gh run download <run-id> --repo lobis/geant4-python-application \
  -n cibw-wheels-ubuntu-latest-x86_64 -D ./g4-wheels
pip install "geant4-python-application[gui]" --find-links ./g4-wheels
```

`--find-links` takes the package from the folder and its dependencies
(including Qt for `[gui]`) from PyPI.

### What the `gui` extra does

The interactive viewer is a separate module that only `Application.visualize()`
loads. Importing the package and running simulations never loads Qt, so
headless machines, containers and clusters need neither Qt nor OpenGL.

The `gui` extra installs Qt from the `PyQt5-Qt5` package; no Homebrew, conda or
system Qt is needed. On Linux, Qt still relies on the system's OpenGL and X11
libraries, which desktop installations already have. Minimal installations may
need them added; the CI tests run on AlmaLinux with:

```bash
dnf install mesa-libGL fontconfig freetype libxkbcommon libxkbcommon-x11 \
  xcb-util-wm xcb-util-image xcb-util-keysyms xcb-util-renderutil dbus-libs
```

On Debian/Ubuntu install the equivalent packages (e.g. `libgl1`,
`libxkbcommon-x11-0` and the `libxcb-*` utility libraries).

`Application.visualization_available()` reports whether the viewer can be
opened, without loading Qt; otherwise `app.visualize()` raises a `RuntimeError`
explaining what is missing. Scripts that open the viewer by default (e.g.
`b1.py`) can run headless with `--batch`.

## Build from source

Needed on platforms without wheels, and for development. Building requires a
Geant4 installation.

### 1. Install Geant4

Via conda:

```bash
conda install -c conda-forge geant4=11.2.2
```

You may also need build tools, e.g. `conda install cmake ninja` (plus
`gxx_linux-64` on Linux).

Or from source, matching the CI configuration:

```bash
git clone https://github.com/Geant4/geant4.git ./geant4-source --depth 1 --branch v11.2.2

cmake -B ./geant4-build -S ./geant4-source \
  -DCMAKE_INSTALL_PREFIX=./geant4-install \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_STANDARD=17 \
  -DGEANT4_USE_GDML=ON \
  -DGEANT4_INSTALL_EXAMPLES=OFF \
  -DGEANT4_INSTALL_DATA=OFF \
  -DGEANT4_BUILD_TLS_MODEL=global-dynamic \
  -DBUILD_STATIC_LIBS=ON \
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_CXX_FLAGS=-fPIC \
  -DCMAKE_C_FLAGS=-fPIC \
  -DGEANT4_USE_SYSTEM_EXPAT=OFF

cmake --build ./geant4-build --parallel $(nproc) --config Release --target install
```

If `xerces-c` is missing, install it from your package manager
(`apt-get install libxerces-c-dev`) or build it from source:

```bash
git clone https://github.com/apache/xerces-c.git ./xerces-source
git -C ./xerces-source checkout tags/v3.2.5

cmake -B ./xerces-build -S ./xerces-source \
  -DCMAKE_INSTALL_PREFIX=./xerces-install \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_STANDARD=17 \
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_CXX_FLAGS=-fPIC \
  -DCMAKE_C_FLAGS=-fPIC \
  -Dnetwork-accessor=socket \
  -Dtranscoder=iconv

cmake --build ./xerces-build --parallel $(nproc) --config Release --target install
```

### 2. Build the package

```bash
pip install git+https://github.com/lobis/geant4-python-application
```

or from a clone:

```bash
git clone https://github.com/lobis/geant4-python-application.git
cd geant4-python-application
pip install .
```

The provided `Dockerfile` also documents the required dependencies:

```bash
docker build -t geant4-python-application .
```

### Qt viewer in source builds

Off by default. It needs a Geant4 built as **shared** libraries with Qt and
OpenGL (e.g. conda-forge `geant4` with `qt[yes]`/`opengl-x11[yes]`); the viewer
then uses that Geant4's Qt:

```bash
pip install . -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON
```

### Building a relocatable macOS wheel yourself

Bundles Geant4, Xerces-C, Expat and other non-system libraries into a wheel
that takes Qt from `PyQt5-Qt5`, like the published wheels:

```bash
PYTHON="$CONDA_PREFIX/bin/python" \
Geant4_DIR=/usr/local/lib/cmake/Geant4 \
tools/build_macos_self_contained.sh
pip install "$(ls dist/self-contained/*.whl)[gui]"
```

The wheel only installs on the macOS version (and newer) that the bundled
Geant4 was built for. The published wheels are built by
`.github/workflows/wheels.yaml`, targeting macOS 11 and manylinux_2_28.

## Data files

Geant4's physics data files (~2 GB) are not part of the wheel. They download
automatically the first time a simulation runs, unless an existing Geant4
installation (found via `geant4-config`) already provides the exact dataset
versions, in which case those are used.

```bash
python -c "import geant4_python_application as g4; print(g4.data_directory())"
```

- Default location, shared by all your Python environments so the data
  downloads only once: `~/Library/Application Support/geant4_python_application`
  on macOS, `~/.local/share/geant4_python_application` on Linux.
- Override the persistent location by setting `GEANT4_PYTHON_APPLICATION_DIR`
  before import, or calling `application_directory(path)` before the
  application initializes.
- Use a temporary directory instead: `application_directory(temp=True)`. If
  the OS partially cleans it up mid-run, delete it manually and let the
  application recreate it.
- Interrupted downloads resume, failed downloads raise an error, and each
  archive's MD5 checksum is verified before it is extracted.
- Uninstalling the package does **not** remove downloaded data files — remove
  them manually.
- For cluster batch jobs, point `application_directory` at a shared location
  to avoid redundant downloads across jobs.
