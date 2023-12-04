from __future__ import annotations

import pathlib

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


def test_geant4_config():
    geant4_config = pathlib.Path(geant4_python_application.geant4_config)
    assert geant4_config.exists()
    assert geant4_config.is_file()

    assert geant4_python_application.check_datasets()
    print(geant4_python_application.datasets())
    geant4_python_application.install_datasets()
