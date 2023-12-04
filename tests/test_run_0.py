from __future__ import annotations

from geant4_python_application import Application, basic_gdml


def test_run():
    app = Application()

    app.setup_manager().setup_detector(gdml=basic_gdml).setup_physics().setup_action()
    app.initialize()
    events = app.run(100)
    assert len(events) == 100
