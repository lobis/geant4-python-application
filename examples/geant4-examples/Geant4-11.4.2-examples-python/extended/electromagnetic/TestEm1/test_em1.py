"""Python adaptation of extended/electromagnetic/TestEm1 process survey."""
from __future__ import annotations
import argparse
from collections import Counter
import awkward as ak
import geant4_python_application as g4

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--material",default="G4_Al"); p.add_argument("--batch",action="store_true"); a=p.parse_args()
    gdml=f'''<gdml><solids><box name="W" x="1000" y="1000" z="1000" lunit="mm"/><box name="A" x="500" y="500" z="500" lunit="mm"/></solids><structure><volume name="ALV"><materialref ref="{a.material}"/><solidref ref="A"/></volume><volume name="World"><materialref ref="G4_Galactic"/><solidref ref="W"/><physvol name="Absorber"><volumeref ref="ALV"/></physvol></volume></structure><setup name="Default" version="1"><world ref="World"/></setup></gdml>'''
    with g4.Application(gdml=gdml,seed=137) as app:
        app.set_event_fields({"id","track_id","step_energy","step_process","step_position","step_track_kinetic_energy"})
        app.commands(["/gun/particle e-","/gun/energy 10 MeV","/gun/position 0 0 -40 cm","/gun/direction 0 0 1"])
        if not a.batch: app.visualize(); return
        events=app.run(a.events)
    processes=Counter(ak.to_list(ak.flatten(events.track.step.process,axis=None)))
    print(f"events: {len(events)}, material: {a.material}, deposited: {float(ak.sum(events.track.step.energy)):.3f} keV")
    print(f"process calls: {dict(processes)}")
if __name__=="__main__": main()
