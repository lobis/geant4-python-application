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


# Compact, self-contained optical geometries used by the Python adaptations of
# Geant4's LXe and WLS examples.  They intentionally model the transport
# concepts rather than the examples' custom PMT/sensitive-detector classes.
lxe_scintillator_gdml = R"""<?xml version="1.0" encoding="UTF-8" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
  <define>
    <matrix coldim="2" name="LXeRINDEX" values="6.2*eV 1.59 7.0*eV 1.61 7.5*eV 1.64"/>
    <matrix coldim="2" name="LXeABSLENGTH" values="6.2*eV 1000 7.5*eV 1000"/>
    <matrix coldim="2" name="LXeSCINT" values="6.2*eV 0.1 7.0*eV 1.0 7.5*eV 0.1"/>
    <matrix coldim="1" name="LXeYIELD" values="120"/>
    <matrix coldim="1" name="LXeRESOLUTION" values="1"/>
    <matrix coldim="1" name="LXeTIME" values="2.2"/>
    <matrix coldim="2" name="GasRINDEX" values="1.0*eV 1.0 8.0*eV 1.0"/>
    <position name="center" unit="mm" x="0" y="0" z="0"/>
  </define>
  <materials>
    <element Z="54" formula="Xe" name="Xenon"><atom value="131.293"/></element>
    <element Z="7" formula="N" name="Nitrogen"><atom value="14.007"/></element>
    <material name="LiquidXenon" state="liquid">
      <property name="RINDEX" ref="LXeRINDEX"/>
      <property name="ABSLENGTH" ref="LXeABSLENGTH"/>
      <property name="SCINTILLATIONCOMPONENT1" ref="LXeSCINT"/>
      <property name="SCINTILLATIONYIELD" ref="LXeYIELD"/>
      <property name="RESOLUTIONSCALE" ref="LXeRESOLUTION"/>
      <property name="SCINTILLATIONTIMECONSTANT1" ref="LXeTIME"/>
      <D unit="g/cm3" value="2.95"/>
      <fraction n="1" ref="Xenon"/>
    </material>
    <material name="NitrogenGas" state="gas">
      <property name="RINDEX" ref="GasRINDEX"/>
      <D unit="g/cm3" value="0.001165"/>
      <fraction n="1" ref="Nitrogen"/>
    </material>
  </materials>
  <solids>
    <box lunit="mm" name="WorldSolid" x="1000" y="1000" z="1000"/>
    <box lunit="mm" name="LXeSolid" x="300" y="300" z="300"/>
    <opticalsurface finish="polished" model="unified" name="LXeSurface" type="dielectric_dielectric" value="1.0"/>
  </solids>
  <structure>
    <volume name="LXeVolume">
      <materialref ref="LiquidXenon"/>
      <solidref ref="LXeSolid"/>
    </volume>
    <volume name="World">
      <materialref ref="NitrogenGas"/>
      <solidref ref="WorldSolid"/>
      <physvol name="lxe"><volumeref ref="LXeVolume"/><positionref ref="center"/></physvol>
    </volume>
    <skinsurface name="LXeSkin" surfaceproperty="LXeSurface"><volumeref ref="LXeVolume"/></skinsurface>
  </structure>
  <setup name="Default" version="1.0"><world ref="World"/></setup>
</gdml>
"""


wls_fiber_gdml = R"""<?xml version="1.0" encoding="UTF-8" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
  <define>
    <matrix coldim="2" name="CoreRINDEX" values="2.0*eV 1.60 4.0*eV 1.60"/>
    <matrix coldim="2" name="CoreABSLENGTH" values="2.0*eV 5000 4.0*eV 5000"/>
    <matrix coldim="2" name="WLSABSLENGTH" values="2.0*eV 5000 2.8*eV 5 4.0*eV 1"/>
    <matrix coldim="2" name="WLSEMISSION" values="2.0*eV 0.1 2.4*eV 1.0 2.8*eV 0.1 4.0*eV 0.0"/>
    <matrix coldim="1" name="WLSTIME" values="0.5"/>
    <matrix coldim="2" name="CladRINDEX" values="2.0*eV 1.49 4.0*eV 1.49"/>
    <matrix coldim="2" name="AirRINDEX" values="2.0*eV 1.0 4.0*eV 1.0"/>
    <position name="center" unit="mm" x="0" y="0" z="0"/>
  </define>
  <materials>
    <element Z="1" formula="H" name="HydrogenWLS"><atom value="1.008"/></element>
    <element Z="6" formula="C" name="CarbonWLS"><atom value="12.011"/></element>
    <material name="WLSCore" state="solid">
      <property name="RINDEX" ref="CoreRINDEX"/>
      <property name="ABSLENGTH" ref="CoreABSLENGTH"/>
      <property name="WLSABSLENGTH" ref="WLSABSLENGTH"/>
      <property name="WLSCOMPONENT" ref="WLSEMISSION"/>
      <property name="WLSTIMECONSTANT" ref="WLSTIME"/>
      <D unit="g/cm3" value="1.05"/>
      <fraction n="0.0774" ref="HydrogenWLS"/><fraction n="0.9226" ref="CarbonWLS"/>
    </material>
    <material name="WLSCladding" state="solid">
      <property name="RINDEX" ref="CladRINDEX"/>
      <D unit="g/cm3" value="1.19"/>
      <fraction n="0.0774" ref="HydrogenWLS"/><fraction n="0.9226" ref="CarbonWLS"/>
    </material>
    <material name="WLSAir" state="gas">
      <property name="RINDEX" ref="AirRINDEX"/>
      <D unit="g/cm3" value="0.0012"/>
      <fraction n="0.0774" ref="HydrogenWLS"/><fraction n="0.9226" ref="CarbonWLS"/>
    </material>
  </materials>
  <solids>
    <box lunit="mm" name="WorldSolid" x="100" y="100" z="500"/>
    <tube aunit="deg" deltaphi="360" lunit="mm" name="CladdingSolid" rmax="1.2" rmin="0" startphi="0" z="400"/>
    <tube aunit="deg" deltaphi="360" lunit="mm" name="CoreSolid" rmax="1.0" rmin="0" startphi="0" z="400"/>
  </solids>
  <structure>
    <volume name="CoreVolume"><materialref ref="WLSCore"/><solidref ref="CoreSolid"/></volume>
    <volume name="CladdingVolume">
      <materialref ref="WLSCladding"/><solidref ref="CladdingSolid"/>
      <physvol name="fiber_core"><volumeref ref="CoreVolume"/><positionref ref="center"/></physvol>
    </volume>
    <volume name="World">
      <materialref ref="WLSAir"/><solidref ref="WorldSolid"/>
      <physvol name="fiber"><volumeref ref="CladdingVolume"/><positionref ref="center"/></physvol>
    </volume>
  </structure>
  <setup name="Default" version="1.0"><world ref="World"/></setup>
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
