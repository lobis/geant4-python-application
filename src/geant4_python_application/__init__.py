from __future__ import annotations

from geant4_python_application._geant4_application import (
    awkward_version,
    geant4_version,
    pybind11_version,
)
from geant4_python_application._version import version, version_tuple
from geant4_python_application.application import Application
from geant4_python_application.detector import Detector
from geant4_python_application.files.datasets import (
    application_data_directory as data_directory,
)
from geant4_python_application.files.datasets import install_datasets
from geant4_python_application.generator import Generator
from geant4_python_application.scoring import NativeScoringMesh, Scoring
from geant4_python_application.files.directories import application_directory
from geant4_python_application.gdml import basic_gdml
from geant4_python_application import optical as optical
from geant4_python_application import cad as cad
from geant4_python_application import io as io
from geant4_python_application import distributed as distributed
from geant4_python_application import geometry as geometry

__version__ = version
__version__tuple__ = version_tuple

__all__ = [
    "Application",
    "Detector",
    "Generator",
    "NativeScoringMesh",
    "Scoring",
    "__version__",
    "__version__tuple__",
    "application_directory",
    "awkward_version",
    "basic_gdml",
    "cad",
    "data_directory",
    "distributed",
    "geant4_version",
    "geometry",
    "install_datasets",
    "io",
    "optical",
    "pybind11_version",
    "version",
]
