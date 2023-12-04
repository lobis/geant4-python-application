from __future__ import annotations

import numpy as np

from geant4_python_application import Application, basic_gdml


def test_seed_single_thread():
    app = Application()

    app.setup_manager()
    app.random_seed = 1100
    app.setup_physics()
    app.setup_detector(gdml=basic_gdml)
    app.setup_action()

    app.initialize()

    assert app.random_seed == 1100

    app.command("/gun/particle e-")
    app.command("/gun/energy 100 MeV")
    app.command("/gun/direction 0 0 -1")
    app.command("/gun/position 0 0 100 cm")

    # launch 100 events
    events = app.run(100)
    assert len(events) == 100
    reference_value = [
        0.00000000e00,
        4.54930276e-01,
        2.25814551e-01,
        8.09506886e-03,
        1.22345221e00,
    ]
    energy = np.array(events["track.step.energy"][0][0][0:5])
    assert np.allclose(energy, reference_value, atol=1e-5)
