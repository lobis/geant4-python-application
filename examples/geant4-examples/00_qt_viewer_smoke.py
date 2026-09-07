"""00 - Qt interactive viewer (requires display, e.g. XQuartz on macOS).

Build with Qt first:
  CMAKE_PREFIX_PATH=/usr/local:/opt/homebrew \
  python -m pip install -e . --no-build-isolation \
    -Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON

Then run this script. A Qt window opens; enter Geant4 commands in its
command panel. Close the window to return (app.visualize blocks).
Run: python 00_qt_viewer_smoke.py
"""
from __future__ import annotations


def main() -> None:
    import geant4_python_application as g4

    print(f"visualization_available = {g4.Application.visualization_available()}")
    assert g4.Application.visualization_available(), "Reinstall with Qt (see docstring)"
    with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
        app.command("/gun/particle e-")
        app.command("/gun/energy 100 MeV")
        app.visualize()  # default: OGL + drawVolume + trajectories


if __name__ == "__main__":
    main()
