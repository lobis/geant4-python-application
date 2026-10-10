"""Python adaptation of extended/radioactivedecay/rdecay01."""
from __future__ import annotations
import argparse
from collections import Counter
import awkward as ak
import geant4_python_application as g4

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--batch",action="store_true"); a=p.parse_args()
    with g4.Application(gdml=g4.basic_gdml,physics="FTFP_BERT",seed=137) as app:
        app.add_physics("G4RadioactiveDecayPhysics")
        app.initialize()  # ion definitions must exist before /gun/ion
        app.commands(["/gun/particle ion","/gun/ion 10 24 0 0","/gun/energy 0 keV","/gun/position 0 0 0 cm"])
        if not a.batch: app.visualize(); return
        events=app.run(a.events)
    particles=Counter(ak.to_list(ak.flatten(events.track.particle,axis=None)))
    print(f"events: {len(events)}, tracked particles: {dict(particles)}")
if __name__=="__main__": main()
