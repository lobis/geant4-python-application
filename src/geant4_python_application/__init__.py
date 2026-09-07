from __future__ import annotations

import os
from pathlib import Path

# A repaired macOS wheel carries Qt's Cocoa platform plugin beside the Python
# package. Point Qt at it before loading the native extension. Source builds
# without a bundled plugin continue to use Qt's normal discovery rules.
_bundled_qt_plugins = Path(__file__).parent / "qt" / "plugins"
if _bundled_qt_plugins.is_dir():
    os.environ.setdefault("QT_PLUGIN_PATH", str(_bundled_qt_plugins))

from geant4_python_application._geant4_application import (
    awkward_version,
    geant4_version,
    pybind11_version,
)
from geant4_python_application._version import version, version_tuple
from geant4_python_application.application import Application
from geant4_python_application.detector import Detector
from geant4_python_application.generator import Generator
from geant4_python_application.scoring import Scoring
from geant4_python_application.files.datasets import data_directory, install_datasets
from geant4_python_application.files.directories import application_directory
from geant4_python_application.gdml import basic_gdml
from geant4_python_application import optical as optical
from geant4_python_application import cad as cad
from geant4_python_application import io as io
from geant4_python_application import distributed as distributed

__version__ = version
__version__tuple__ = version_tuple

__all__ = [
    "__version__",
    "__version__tuple__",
    "geant4_version",
    "awkward_version",
    "pybind11_version",
    "version",
    "Application",
    "Detector",
    "Generator",
    "Scoring",
    "basic_gdml",
    "install_datasets",
    "data_directory",
    "application_directory",
    "optical",
    "cad",
    "io",
    "distributed",
]
