"""01 - Reference physics-list selection.

Shows listing Geant4 reference lists, running with FTFP_BERT vs custom,
and handling an unknown list name.
Run: python 01_reference_physics_lists.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import geant4_python_application as g4

    lists = g4.Application.available_physics_lists()
    print(f"Available physics lists: {len(lists)}")
    print(f"Sample: {lists[:6]}")
    assert "custom" in lists
    assert "FTFP_BERT" in lists

    # Reference list
    with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=11) as app:
        events = app.run(2)
        print(f"FTFP_BERT: ran {len(events)} events")

    # Default custom list (EmOption4 + FTFP_BERT hadronic)
    with g4.Application(gdml=g4.basic_gdml, physics="custom", seed=11) as app:
        events = app.run(2)
        print(f"custom: ran {len(events)} events")

    # Unknown name raises
    try:
        with g4.Application(gdml=g4.basic_gdml, physics="NOT_A_LIST") as app:
            app.run(1)
    except Exception as exc:
        print(f"Unknown list correctly raised: {type(exc).__name__}: {exc}")

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, physics="FTFP_BERT", seed=11) as app:
            app.command("/gun/particle gamma")
            app.command("/gun/energy 2 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
