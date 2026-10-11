from __future__ import annotations

import geant4_python_application as g4


def main():
    with g4.Application(gdml=g4.basic_gdml, seed=137) as app:
        app.commands(
            [
                "/gun/particle e-",
                "/gun/energy 100 MeV",
                "/gun/direction 0 0 -1",
                "/gun/position 0 0 40 cm",
            ]
        )
        app.visualize()


if __name__ == "__main__":
    main()
