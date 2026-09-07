"""06 - Python run/event/track/step callbacks.

Shows Application.run_with_callbacks() - an offline callback layer over
the awkward event model (on_run / on_event / on_track / on_step).
Run: python 06_callbacks.py
"""
from __future__ import annotations


def main() -> None:
    import sys

    import geant4_python_application as g4

    counts = {"run": 0, "event": 0, "track": 0, "step": 0}

    def on_run(events) -> None:
        counts["run"] += 1
        print(f"on_run: {len(events)} events")

    def on_event(event) -> None:
        counts["event"] += 1

    def on_track(track, event) -> None:
        counts["track"] += 1

    def on_step(step, track, event) -> None:
        counts["step"] += 1

    with g4.Application(gdml=g4.basic_gdml, seed=16) as app:
        app.command("/gun/particle gamma")
        app.command("/gun/energy 1 MeV")
        events = app.run_with_callbacks(
            3, on_run=on_run, on_event=on_event, on_track=on_track, on_step=on_step
        )
        print(f"ran {len(events)} events")

    print(f"callback counts: {counts}")
    assert counts["run"] == 1 and counts["event"] == 3
    assert counts["track"] > 0 and counts["step"] > 0

    if "--vis" in sys.argv:
        with g4.Application(gdml=g4.basic_gdml, seed=16) as app:
            app.command("/gun/particle gamma")
            app.command("/gun/energy 1 MeV")
            app.visualize()  # Qt viewer; close window to return


if __name__ == "__main__":
    main()
