import geant4
import pytest


def test_setup_and_run():
    app = geant4.Application()
    app.setup_manager()
    app.setup_detector()
    app.setup_physics()
    app.setup_action()
    app.initialize()
    app.run()


def test_missing_setup():
    app = geant4.Application()

    with pytest.raises(RuntimeError):
        app.initialize()


def test_missing_manager():
    app = geant4.Application()

    with pytest.raises(RuntimeError):
        app.setup_detector()
