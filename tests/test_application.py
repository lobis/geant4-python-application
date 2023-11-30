import geant4
import pytest

import numpy as np


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


# This may not hold for all Geant4 versions
def test_seed_single_thread():
    app = geant4.Application()

    app.setup_manager()
    app.set_random_seed(137)
    app.setup_physics()
    app.setup_detector()
    app.setup_action()

    app.initialize()

    # launch 100 events
    events = app.run(100)
    assert len(events) == 100

    reference_value = [
        113.52462,
        124.65908,
        98.72738,
        130.19978,
        65.732864,
        72.24915,
        58.46046,
        40.267754,
        47.890503,
        42.38143,
        25.019478,
        34.674374,
        21.276197,
        24.153574,
        12.234435,
        31.175776,
        15.838588,
        11.047329,
        18.216051,
        12.271155,
    ]

    energy = np.array(events["track.hits.energy"][0][0])

    assert np.allclose(energy, reference_value, atol=1e-5)
