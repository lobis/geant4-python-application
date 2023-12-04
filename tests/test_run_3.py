from __future__ import annotations

import requests

from geant4_python_application import Application


def test_complex_gdml():
    url = "https://raw.githubusercontent.com/rest-for-physics/restG4/dc3a8f42cea4978206a13325261fa85ec1b26261/examples/13.IAXO/geometry/setup.gdml"

    app = Application()

    app.setup_manager()
    app.setup_physics()
    app.setup_detector(gdml=requests.get(url).text)
    app.setup_action()

    app.detector.sensitive_volumes = {"gasVolume"}

    app.initialize()

    # primary generator action can be modified after initialization
    app.generator.set_particle("neutron")
    app.generator.set_energy(100)
    app.generator.set_position((0, 0, 1e3))
    app.generator.set_direction((0, 0, -1))

    assert len(app.detector.logical_volumes) == 22
    assert len(app.detector.physical_volumes) == 309

    events = app.run(1)
    print(events)
