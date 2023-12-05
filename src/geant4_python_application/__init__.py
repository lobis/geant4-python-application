from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import warnings

geant4_config = shutil.which("geant4-config")

if geant4_config is None:
    raise ImportError(
        "Could not find geant4-config. Please make sure Geant4 is installed and sourced."
    )

_geant4_version = subprocess.check_output(
    [geant4_config, "--version"], encoding="utf-8"
).strip()

_geant4_libs = subprocess.check_output(
    [geant4_config, "--libs"], encoding="utf-8"
).strip()

_geant4_prefix = subprocess.check_output(
    [geant4_config, "--prefix"], encoding="utf-8"
).strip()

_geant4_libs_dir = os.path.join(_geant4_prefix, "lib")


def load_libs():
    for lib in _geant4_libs.split():
        if not lib.startswith("-l"):
            continue
        # lib has format -l<libname>, transform to file name which is lib<libname>
        library_absolute_path = os.path.join(_geant4_libs_dir, "lib" + lib[2:])
        if sys.platform == "darwin":
            library_absolute_path += ".dylib"
        elif sys.platform == "linux":
            library_absolute_path += ".so"
        else:
            raise RuntimeError("Unsupported platform: ", sys.platform)

        if not os.path.exists(library_absolute_path):
            raise ImportError(
                f"Could not find library {lib} ({library_absolute_path}) in {_geant4_libs_dir}."
            )

        try:
            ctypes.cdll.LoadLibrary(library_absolute_path)
        except Exception as e:
            warnings.warn(
                f"Could not load library: {library_absolute_path}. Error: {e}"
            )


def datasets() -> list[(str, str, str)]:
    _datasets = subprocess.check_output(
        [geant4_config, "--datasets"], encoding="utf-8"
    ).strip()
    return [tuple(line.split()) for line in _datasets.split("\n") if line.strip() != ""]


def check_datasets() -> bool:
    dataset_dirs = [dataset[2] for dataset in datasets()]
    return all([os.path.exists(dataset_dir) for dataset_dir in dataset_dirs])


def install_datasets(always: bool = False) -> None:
    if not always and check_datasets():
        return
    subprocess.run([geant4_config, "--install-datasets"], check=True)


_minimum_geant4_version = "11.1.0"


def _parse_geant4_version(version: str) -> (int, int, int):
    return tuple([int(part) for part in version.split(".")])


try:
    available_geant4_version_parsed = _parse_geant4_version(_geant4_version)
    minimum_geant4_version_parsed = _parse_geant4_version(_minimum_geant4_version)
    if available_geant4_version_parsed < minimum_geant4_version_parsed:
        warnings.warn(
            f"Geant4 version {_geant4_version} is lower than the minimum required version {_minimum_geant4_version}."
        )
except Exception as e:
    raise RuntimeError(
        f"Error comparing Geant4 version '{_geant4_version}' with '{_minimum_geant4_version}': {e}"
    )

try:
    load_libs()
except Exception as e:
    print(f"Could not load Geant4 dynamic libraries: {e}")

# environment variable GEANT4_DATA_DIR is a recent addition to Geant4
if "GEANT4_DATA_DIR" not in os.environ:
    os.environ["GEANT4_DATA_DIR"] = os.path.join(
        _geant4_prefix, "share", "Geant4", "data"
    )

_geant4_data_dir = os.environ["GEANT4_DATA_DIR"]
if not os.path.exists(_geant4_data_dir) or not os.listdir(_geant4_data_dir):
    warnings.warn(
        f"""Geant4 data directory {_geant4_data_dir} does not exist or is empty. Please set the
    GEANT4_DATA_DIR environment variable to the correct directory or install the datasets via `geant4-config
    --install-datasets` or calling `geant4_python_application.install_datasets()`."""
    )

from geant4_python_application.gdml import basic_gdml
from geant4_python_application.geant4_application import (
    Application,
    PrimaryGeneratorAction,
    StackingAction,
    __awkward_version__,
    __doc__,
    __geant4_version__,
    __pybind11_version__,
    __version__,
)

if _geant4_version != __geant4_version__:
    warnings.warn(
        f"""Geant4 version mismatch. Python module was compiled with Geant4 version {__geant4_version__}
        , but the available Geant4 version is {_geant4_version}."""
    )

__all__ = [
    "__doc__",
    "__version__",
    "__geant4_version__",
    "__awkward_version__",
    "__pybind11_version__",
    "Application",
    "PrimaryGeneratorAction",
    "StackingAction",
    "basic_gdml",
]
