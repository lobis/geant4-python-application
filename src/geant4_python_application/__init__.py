from __future__ import annotations

from geant4_python_application.datasets import install_datasets
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


def _setup_manager(self, *args, **kwargs):
    install_datasets()
    self._setup_manager(*args, **kwargs)


Application._setup_manager = Application.setup_manager
Application.setup_manager = _setup_manager
