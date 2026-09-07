from __future__ import annotations

"""Minimal optical-materials/surfaces helpers (GDML-based).

Geant4 optical properties (RINDEX, scintillation, WLS, ...) and optical
surfaces (skin/border) are defined in GDML via <matrix>, <property> and
<opticalsurface>/<skinsurface>/<bordersurface> tags. This module provides a
compact, fast-simulating water-scintillator GDML example plus UI-command
helpers for tuning optical processes at run time.
"""

optical_water_gdml = R"""<?xml version="1.0" encoding="UTF-8" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
  <define>
    <matrix coldim="2" name="WATERRINDEX" values="2.034*eV 1.3435 3.026*eV 1.3545 4.136*eV 1.3608"/>
    <matrix coldim="2" name="WATERABSLENGTH" values="2.034*eV 20000 4.136*eV 14500"/>
    <matrix coldim="2" name="SCINTCOMP" values="2.034*eV 1 3.026*eV 1 4.136*eV 1"/>
    <matrix coldim="1" name="SCINTYIELD" values="50"/>
    <matrix coldim="1" name="RESOLUTIONSCALE" values="1"/>
    <matrix coldim="1" name="TIMECONSTANT1" values="1"/>
    <position name="center" unit="mm" x="0" y="0" z="0"/>
  </define>
  <materials>
    <element Z="1" formula="H" name="Hydrogen"><atom value="1.01"/></element>
    <element Z="8" formula="O" name="Oxygen"><atom value="16.0"/></element>
    <material name="WaterScint" state="liquid">
      <property name="RINDEX" ref="WATERRINDEX"/>
      <property name="ABSLENGTH" ref="WATERABSLENGTH"/>
      <property name="SCINTILLATIONCOMPONENT1" ref="SCINTCOMP"/>
      <property name="SCINTILLATIONYIELD" ref="SCINTYIELD"/>
      <property name="RESOLUTIONSCALE" ref="RESOLUTIONSCALE"/>
      <property name="SCINTILLATIONTIMECONSTANT1" ref="TIMECONSTANT1"/>
      <D unit="g/cm3" value="1"/>
      <fraction n="0.1119" ref="Hydrogen"/>
      <fraction n="0.8881" ref="Oxygen"/>
    </material>
    <material name="AirOpt" state="gas">
      <D unit="g/cm3" value="0.00129"/>
      <fraction n="0.7" ref="Hydrogen"/>
      <fraction n="0.3" ref="Oxygen"/>
    </material>
  </materials>
  <solids>
    <box lunit="mm" name="WorldSolid" x="1000" y="1000" z="1000"/>
    <box lunit="mm" name="ScintSolid" x="500" y="500" z="500"/>
    <opticalsurface finish="polished" model="glisur" name="ScintSurface" type="dielectric_dielectric" value="1.0"/>
  </solids>
  <structure>
    <volume name="ScintVolume">
      <materialref ref="WaterScint"/>
      <solidref ref="ScintSolid"/>
    </volume>
    <volume name="World">
      <materialref ref="AirOpt"/>
      <solidref ref="WorldSolid"/>
      <physvol name="scint">
        <volumeref ref="ScintVolume"/>
        <positionref ref="center"/>
      </physvol>
    </volume>
    <skinsurface name="ScintSkin" surfaceproperty="ScintSurface">
      <volumeref ref="ScintVolume"/>
    </skinsurface>
  </structure>
  <setup name="Default" version="1.0">
    <world ref="World"/>
  </setup>
</gdml>
"""

#: Common optical-process UI commands for Geant4 11.2 (apply via app.commands(...)).
#: Verified against /process/optical/scintillation and /process/optical/cerenkov.
optical_tuning_commands = [
    "/process/optical/scintillation/setStackPhotons true",
    "/process/optical/cerenkov/setMaxPhotons 100",
    "/process/optical/verbose 1",
]


def scintillation_commands(stack_photons: bool = True, max_cerenkov: int = 100) -> list[str]:
    """Return UI commands tuning scintillation/Cerenkov at run time (Geant4 11.2)."""
    return [
        f"/process/optical/scintillation/setStackPhotons {'true' if stack_photons else 'false'}",
        f"/process/optical/cerenkov/setMaxPhotons {max_cerenkov}",
    ]
