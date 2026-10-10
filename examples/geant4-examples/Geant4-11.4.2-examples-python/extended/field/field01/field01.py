"""Python adaptation of extended/field/field01 magnetic tracking study."""
from __future__ import annotations
import argparse
import awkward as ak
import geant4_python_application as g4

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--field",type=float,default=1.0); p.add_argument("--batch",action="store_true"); a=p.parse_args()
    with g4.Application(gdml=g4.basic_gdml,seed=137) as app:
        app.detector.magnetic_field=(0.0,a.field,0.0)
        app.set_event_fields({"id","track_id","step_position","step_volume","step_track_kinetic_energy"})
        app.commands(["/gun/particle e-","/gun/energy 100 MeV","/gun/position 0 0 -20 cm","/gun/direction 0 0 1"])
        if not a.batch: app.visualize(); return
        events=app.run(a.events)
    nsteps=len(ak.flatten(events.track.step.position.x,axis=None))
    print(f"events: {len(events)}, B=(0,{a.field},0) T, recorded steps: {nsteps}")
if __name__=="__main__": main()
