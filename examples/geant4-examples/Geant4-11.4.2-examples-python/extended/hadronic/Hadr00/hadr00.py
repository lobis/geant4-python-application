"""Python adaptation of extended/hadronic/Hadr00 target interactions."""
from __future__ import annotations
import argparse
from collections import Counter
import awkward as ak
import geant4_python_application as g4

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--physics",default="FTFP_BERT"); p.add_argument("--batch",action="store_true"); a=p.parse_args()
 gdml='''<gdml><solids><box name="W" x="500" y="500" z="1000" lunit="mm"/><tube name="T" rmin="0" rmax="10" z="200" startphi="0" deltaphi="360" aunit="deg" lunit="mm"/></solids><structure><volume name="TLV"><materialref ref="G4_Pb"/><solidref ref="T"/></volume><volume name="World"><materialref ref="G4_AIR"/><solidref ref="W"/><physvol name="Target"><volumeref ref="TLV"/></physvol></volume></structure><setup name="Default" version="1"><world ref="World"/></setup></gdml>'''
 with g4.Application(gdml=gdml,physics=a.physics,seed=137) as app:
  app.commands(["/gun/particle proton","/gun/energy 15 GeV","/gun/position 0 0 -9 cm","/gun/direction 0 0 1"])
  if not a.batch: app.visualize(); return
  events=app.run(a.events)
 secondaries=events.track.particle[events.track.parent_id>0]
 counts=Counter(ak.to_list(ak.flatten(secondaries,axis=None)))
 print(f"events: {len(events)}, physics: {a.physics}, secondaries: {dict(counts)}")
if __name__=="__main__": main()
