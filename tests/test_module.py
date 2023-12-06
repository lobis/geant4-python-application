from __future__ import annotations

import geant4_python_application


def test_imports():
    assert geant4_python_application.__doc__
    assert geant4_python_application.__version__
    awkward_version = geant4_python_application.__awkward_version__
    assert awkward_version
    pybind11_version = geant4_python_application.__pybind11_version__
    assert pybind11_version
    geant4_version = geant4_python_application.__geant4_version__
    assert geant4_version
