from __future__ import annotations

import awkward as ak
import numpy as np
import pytest

from geant4_python_application import Application

gold_slab_gdml = """<?xml version="1.0" encoding="UTF-8"?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
    <solids>
        <box name="WorldSolid" x="100" y="100" z="100" lunit="cm"/>
        <box name="SlabSolid" x="10" y="10" z="0.1" lunit="mm"/>
    </solids>
    <structure>
        <volume name="Slab">
            <materialref ref="G4_Au"/>
            <solidref ref="SlabSolid"/>
        </volume>
        <volume name="World">
            <materialref ref="G4_Galactic"/>
            <solidref ref="WorldSolid"/>
            <physvol name="slab">
                <volumeref ref="Slab"/>
            </physvol>
        </volume>
    </structure>
    <setup name="Default" version="1.0">
        <world ref="World"/>
    </setup>
</gdml>
"""


@pytest.mark.parametrize("n_threads", [0, 2])
def test_gold_fluorescence(n_threads):
    # The default physics list enables fluorescence; it was silently inactive while
    # G4RadioactiveDecayPhysics was registered before the EM constructor.
    if n_threads > 0 and not Application.multithreading_available():
        pytest.skip("linked Geant4 runtime was built without multithreading")
    with Application(gdml=gold_slab_gdml, seed=1234, n_threads=n_threads) as app:
        app.generator.particle("gamma").energy(100, "keV")
        app.generator.position(0, 0, -10, "cm").direction(0, 0, 1)
        events = app.run(500)

    particle = ak.flatten(events.track.particle)
    creator = ak.flatten(events.track.creator_process)
    energy = np.asarray(ak.flatten(events.track.initial_energy))  # keV

    photoelectrons = ak.sum((particle == "e-") & (creator == "phot"))
    fluorescence = energy[np.asarray((particle == "gamma") & (creator == "phot"))]
    # Gold K-alpha lines are at 66.99 and 68.80 keV (K-shell binding 80.7 keV).
    k_alpha = fluorescence[(fluorescence > 66) & (fluorescence < 70)]

    # About 60% of the photons interact in 0.1 mm of gold, almost all by
    # photoabsorption, 80% of it in the K shell, with a 96% fluorescence yield.
    assert photoelectrons > 250
    assert len(k_alpha) > 100
    assert np.all(fluorescence < 100)
