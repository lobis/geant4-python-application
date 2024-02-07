from __future__ import annotations

import geant4_python_application


def test_imports():
    assert geant4_python_application.__version__
    assert geant4_python_application.version
    awkward_version = geant4_python_application.awkward_version
    assert awkward_version
    pybind11_version = geant4_python_application.pybind11_version
    assert pybind11_version
    geant4_version = geant4_python_application.geant4_version
    assert geant4_version
    assert geant4_python_application
    assert geant4_python_application.Application
    assert geant4_python_application.Detector
