"""Python adaptation of the NRCC electron-scattering benchmark geometry."""
from __future__ import annotations
import argparse
import awkward as ak
import geant4_python_application as g4

GDML='''<gdml><solids><box name="W" x="400" y="400" z="800" lunit="mm"/><tube name="F" rmin="0" rmax="50" z="0.1" startphi="0" deltaphi="360" aunit="deg" lunit="mm"/><box name="S" x="300" y="300" z="1" lunit="mm"/></solids><structure><volume name="FLV"><materialref ref="G4_Ta"/><solidref ref="F"/></volume><volume name="SLV"><materialref ref="G4_AIR"/><solidref ref="S"/></volume><volume name="World"><materialref ref="G4_AIR"/><solidref ref="W"/><physvol name="ScatterFoil"><volumeref ref="FLV"/><position unit="mm" x="0" y="0" z="-100"/></physvol><physvol name="ScoringPlane"><volumeref ref="SLV"/><position unit="mm" x="0" y="0" z="100"/></physvol></volume></structure><setup name="Default" version="1"><world ref="World"/></setup></gdml>'''

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=1000); p.add_argument("--batch",action="store_true"); a=p.parse_args()
 with g4.Application(gdml=GDML,seed=137) as app:
  app.set_event_fields({"id","track_id","step_volume_post","step_momentum","step_position"})
  app.commands(["/gun/particle e-","/gun/energy 13 MeV","/gun/position 0 0 -30 cm","/gun/direction 0 0 1"])
  if not a.batch: app.visualize(); return
  events=app.run(a.events)
 step=events.track.step; crossing=step[step.volume_post=="ScoringPlane"]
 n=len(ak.flatten(crossing.position.x,axis=None))
 print(f"events: {len(events)}, scoring-plane crossings: {n}")
if __name__=="__main__": main()
