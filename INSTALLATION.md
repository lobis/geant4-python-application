# Installation

This package is not yet published on PyPI, so install from source. Building
requires a system Geant4 installation as a build dependency.

## From source

### 1. Install Geant4

Via conda:

```bash
conda install -c conda-forge geant4
```

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
git clone https://github.com/lobis/geant4-python-application.git
cd geant4-python-application
pip install .
```

Or use the provided `Dockerfile`, which also documents the required
dependencies:

```bash
docker build -t geant4-python-application .
```

### Qt visualization

Off by default. Enable it at install time (requires Geant4 built with
Qt/OpenGL, e.g. conda-forge `geant4` with `qt[yes]`/`opengl-x11[yes]`):

```bash
pip install --force-reinstall --no-deps . -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON
```

Without it, `app.visualize()` raises `RuntimeError: Visualization support was
not built`. Scripts that default to visualization (e.g. `b1.py`) can be run
headless instead with `--batch`.

### Relocatable macOS wheel

Bundles Geant4, Xerces-C, Expat, and non-system transitive libraries into the
wheel:

```bash
PYTHON="$CONDA_PREFIX/bin/python" \
Geant4_DIR=/usr/local/lib/cmake/Geant4 \
tools/build_macos_self_contained.sh
```

Install from `dist/self-contained/repaired`. Geant4 datasets (~2 GB) stay
outside the wheel and download on first use. Homebrew's Qt 5 remains an
external framework dependency; a fully standalone GUI build needs Qt built as
non-framework dylibs or linked statically.

## Data files

Geant4's physics data files are not bundled in the wheel and are downloaded
automatically on first use.

```bash
python -c "import geant4_python_application; print(geant4_python_application.get_data_path())"
```

- Default location: `$CONDA_PREFIX/share/geant4_python_application` (or the
  equivalent `sys.prefix` for a venv).
- Override the persistent location by setting `GEANT4_PYTHON_APPLICATION_DIR`
  before import, or calling `application_directory(path)` before the
  application initializes.
- Use a temporary directory instead: `application_directory(temp=True)`. If
  the OS partially cleans it up mid-run, delete it manually and let the
  application recreate it.
- Uninstalling the package does **not** remove downloaded data files — remove
  them manually.
- For cluster batch jobs, point `application_directory` at a shared location
  to avoid redundant downloads across jobs.
