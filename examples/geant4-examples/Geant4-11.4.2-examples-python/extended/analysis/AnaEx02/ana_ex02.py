"""Python adaptation of AnaEx02 with nested Parquet event output."""
from __future__ import annotations
import argparse
from pathlib import Path
import geant4_python_application as g4

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--batch",action="store_true"); p.add_argument("-o","--output",type=Path,default=Path("ana_ex02.parquet")); a=p.parse_args()
    with g4.Application(gdml=g4.basic_gdml,physics="FTFP_BERT",seed=138) as app:
        app.commands(["/gun/particle e-","/gun/energy 100 MeV","/gun/position 0 0 -40 cm","/gun/direction 0 0 1"])
        if not a.batch: app.visualize(); return
        events=app.run(a.events)
    g4.io.events_to_parquet(events,a.output)
    assert len(g4.io.events_from_parquet(a.output))==len(events)
    print(f"events: {len(events)}, wrote {a.output}")
if __name__=="__main__": main()
