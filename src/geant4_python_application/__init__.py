from __future__ import annotations

import os
import sys
import ctypes
import subprocess
import shutil
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

for lib in _geant4_libs.split()[1:]:
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
        print("Could not load library: ", library_absolute_path)
        print("Exception: ", e)
        raise e


def datasets() -> list[(str, str, str)]:
    datasets = subprocess.check_output(
        [geant4_config, "--datasets"], encoding="utf-8"
    ).strip()
    return [
        tuple(line.split()) for line in datasets.split("\n") if line.strip() != ""
    ]


def check_datasets() -> bool:
    dataset_dirs = [dataset[2] for dataset in datasets()]
    return all([os.path.exists(dataset_dir) for dataset_dir in dataset_dirs])


def install_datasets(always: bool = False) -> None:
    if not always and check_datasets():
        return
    subprocess.run([geant4_config, "--install-datasets"], check=True)


from geant4_python_application._core import (
    Application,
    PrimaryGeneratorAction,
    StackingAction,
    __doc__,
    __geant4_version__,
    __version__,
)
from geant4_python_application.gdml import basic_gdml

if _geant4_version != __geant4_version__:
    warnings.warn(
        f"Geant4 version mismatch. Python module was compiled with Geant4 version {__geant4_version__}, but the available Geant4 version is {geant4_version}."
    )

__all__ = [
    "__doc__",
    "__version__",
    "__geant4_version__",
    "Application",
    "PrimaryGeneratorAction",
    "StackingAction",
    "basic_gdml",
]
