from __future__ import annotations

from geant4_python_application import Application, basic_gdml


def test_event_data_is_cleared():
    app = Application()

    app.setup_manager()
    app.setup_physics()
    app.setup_detector(gdml=basic_gdml)
    app.setup_action()

    app.initialize()

    for _ in range(10):
        events = app.run(100)
        assert len(events) == 100
