from __future__ import annotations

import pytest

import geant4_python_application
from geant4_python_application import Application


def test_imports():
    assert Application
    assert geant4_python_application
    assert geant4_python_application.Application
    assert geant4_python_application.PrimaryGeneratorAction
    assert geant4_python_application.StackingAction


def test_missing_setup():
    app = Application()

    with pytest.raises(RuntimeError):
        app.initialize()


def test_missing_manager():
    app = Application()

    with pytest.raises(RuntimeError):
        app.setup_detector(gdml="")
        app.setup_detector()


def test_multiple_apps():
    # Could this work somehow?
    with pytest.raises(RuntimeError):
        for _ in range(10):
            app = Application()
