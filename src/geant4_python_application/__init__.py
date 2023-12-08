from __future__ import annotations

from geant4_python_application._geant4_application import (
    __doc__,
    __version__,
    awkward_version,
    geant4_version,
    pybind11_version,
)
from geant4_python_application.application import Application
from geant4_python_application.datasets import data_dir, install_datasets
from geant4_python_application.detector import Detector
from geant4_python_application.gdml import basic_gdml

version = __version__

__all__ = [
    "__doc__",
    "__version__",
    "geant4_version",
    "awkward_version",
    "pybind11_version",
    "version",
    "Application",
    "Detector",
    "basic_gdml",
    "data_dir",
    "install_datasets",
]
