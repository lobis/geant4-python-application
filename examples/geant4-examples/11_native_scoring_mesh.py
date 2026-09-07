"""11 - Native Geant4 scoring mesh through the Python command interface."""

from __future__ import annotations

from pathlib import Path

import geant4_python_application as g4


def main() -> None:
    output = Path("native_energy_mesh.csv")
    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=22) as app:
        mesh = g4.NativeScoringMesh(app, "waterMesh", "energyDeposit")
        mesh.box((250, 250, 250), (10, 10, 10), unit="mm")
        app.commands(["/gun/particle e-", "/gun/energy 10 MeV"])
        app.run(10)
        mesh.dump(output)
    assert output.exists() and output.stat().st_size > 0
    print(f"native Geant4 scoring mesh written to {output.resolve()}")


if __name__ == "__main__":
    main()
