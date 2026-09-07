from __future__ import annotations

"""CAD -> GDML helpers via tessellated solids (no external CAD kernel).

Provides:
- mesh_to_gdml(vertices, faces): build GDML with a <tessellated> solid.
- stl_ascii_to_gdml(stl_text): parse ASCII STL -> GDML (triangles only).
Both produce a self-contained GDML string with world box + placed volume,
suitable for Application(gdml=...).
"""


def mesh_to_gdml(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int]],
    *,
    name: str = "cad_solid",
    material: str = "G4_WATER",
    world_size_mm: float = 1000.0,
    unit: str = "mm",
) -> str:
    if len(vertices) == 0 or len(faces) == 0:
        msg = "vertices and faces must be non-empty"
        raise ValueError(msg)
    pos_lines = []
    for i, (x, y, z) in enumerate(vertices):
        pos_lines.append(
            f'  <position name="v{i}" unit="{unit}" x="{x}" y="{y}" z="{z}" />'
        )
    tri_lines = []
    for a, b, c in faces:
        if min(a, b, c) < 0 or max(a, b, c) >= len(vertices):
            msg = f"face index out of range: {(a, b, c)}"
            raise ValueError(msg)
        tri_lines.append(
            f'   <triangular vertex1="v{a}" vertex2="v{b}" vertex3="v{c}" />'
        )
    positions = "\n".join(pos_lines)
    triangles = "\n".join(tri_lines)
    return f"""<?xml version="1.0" encoding="UTF-8" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">
 <define>
{positions}
  <position name="cadpos" unit="{unit}" x="0" y="0" z="0" />
 </define>
 <materials>
  <element Z="1" formula="H" name="H"><atom value="1.0"/></element>
 </materials>
 <solids>
  <box lunit="{unit}" name="world" x="{world_size_mm}" y="{world_size_mm}" z="{world_size_mm}" />
  <tessellated aunit="degree" lunit="{unit}" name="{name}">
{triangles}
  </tessellated>
 </solids>
 <structure>
  <volume name="CadVolume">
   <materialref ref="{material}"/>
   <solidref ref="{name}"/>
  </volume>
  <volume name="World">
   <materialref ref="G4_AIR"/>
   <solidref ref="world"/>
   <physvol name="cad">
    <volumeref ref="CadVolume"/>
    <positionref ref="cadpos"/>
   </physvol>
  </volume>
 </structure>
 <setup name="Default" version="1.0"><world ref="World"/></setup>
</gdml>
"""


def cube_mesh(size_mm: float = 100.0) -> tuple[list, list]:
    """Return (vertices, faces) for an axis-aligned cube centred at origin."""
    h = size_mm / 2.0
    v = [
        (-h, -h, -h), (h, -h, -h), (h, h, -h), (-h, h, -h),
        (-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h),
    ]
    f = [
        (0, 1, 2), (0, 2, 3),  # -z
        (4, 6, 5), (4, 7, 6),  # +z
        (0, 4, 5), (0, 5, 1),  # -y
        (3, 2, 6), (3, 6, 7),  # +y
        (0, 3, 7), (0, 7, 4),  # -x
        (1, 5, 6), (1, 6, 2),  # +x
    ]
    return v, f


def stl_ascii_to_gdml(stl_text: str, **kwargs) -> str:
    """Parse minimal ASCII STL (facet normal/vertex lines) into GDML."""
    verts: list[tuple[float, float, float]] = []
    index: dict[tuple[float, float, float], int] = {}
    faces: list[tuple[int, int, int]] = []
    cur: list[int] = []
    for line in stl_text.splitlines():
        s = line.strip().split()
        if len(s) >= 4 and s[0] == "vertex":
            p = (float(s[1]), float(s[2]), float(s[3]))
            if p not in index:
                index[p] = len(verts)
                verts.append(p)
            cur.append(index[p])
            if len(cur) == 3:
                faces.append((cur[0], cur[1], cur[2]))
                cur = []
    if not faces:
        msg = "no facets parsed from STL text"
        raise ValueError(msg)
    return mesh_to_gdml(verts, faces, **kwargs)
