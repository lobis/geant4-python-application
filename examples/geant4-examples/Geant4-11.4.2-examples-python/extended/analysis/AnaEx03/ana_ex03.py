"""Python adaptation of AnaEx03 with ROOT summary output via uproot."""
from __future__ import annotations
import argparse
from pathlib import Path
import geant4_python_application as g4

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--batch",action="store_true"); p.add_argument("-o","--output",type=Path,default=Path("ana_ex03.root")); a=p.parse_args()
    with g4.Application(gdml=g4.basic_gdml,physics="FTFP_BERT",seed=139) as app:
        app.commands(["/gun/particle gamma","/gun/energy 10 MeV","/gun/position 0 0 -40 cm","/gun/direction 0 0 1"])
        if not a.batch: app.visualize(); return
        events=app.run(a.events)
    try:
        g4.io.events_to_root(events,a.output)
        assert len(g4.io.events_from_root(a.output)["id"])==len(events)
        print(f"events: {len(events)}, wrote {a.output}")
    except ImportError as exc:
        print(f"events: {len(events)}, ROOT output skipped: {exc}")
if __name__=="__main__": main()
