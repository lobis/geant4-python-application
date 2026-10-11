from __future__ import annotations

"""Pure-Python GDML geometry generators.

These helpers expand regular layouts into ordinary GDML placements.  They are
useful where an official example uses a live ``G4VPVParameterisation`` callback:
the geometry is equivalent at initialization time, but there is no callback
during tracking.
"""


def linear_array_gdml(
    count: int,
    *,
    spacing_mm: float = 20.0,
    box_size_mm: float = 10.0,
    material: str = "G4_Si",
    world_material: str = "G4_AIR",
) -> str:
    """Return GDML containing ``count`` equally spaced boxes along x."""
    if count < 1:
        raise ValueError("count must be at least one")
    if spacing_mm <= 0 or box_size_mm <= 0:
        raise ValueError("spacing_mm and box_size_mm must be positive")
    extent = (count - 1) * spacing_mm + box_size_mm
    world_x = max(100.0, extent + 4.0 * spacing_mm)
    placements = []
    x0 = -0.5 * (count - 1) * spacing_mm
    for index in range(count):
        x = x0 + index * spacing_mm
        placements.append(
            f'''      <physvol name="cell_{index}">
        <volumeref ref="CellVolume"/>
        <position name="cell_position_{index}" unit="mm" x="{x:.12g}" y="0" z="0"/>
      </physvol>'''
        )
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
  <solids>
    <box name="WorldSolid" lunit="mm" x="{world_x:.12g}" y="100" z="100"/>
    <box name="CellSolid" lunit="mm" x="{box_size_mm:.12g}" y="40" z="40"/>
  </solids>
  <structure>
    <volume name="CellVolume"><materialref ref="{material}"/><solidref ref="CellSolid"/></volume>
    <volume name="World">
      <materialref ref="{world_material}"/><solidref ref="WorldSolid"/>
{chr(10).join(placements)}
    </volume>
  </structure>
  <setup name="Default" version="1.0"><world ref="World"/></setup>
</gdml>
'''
