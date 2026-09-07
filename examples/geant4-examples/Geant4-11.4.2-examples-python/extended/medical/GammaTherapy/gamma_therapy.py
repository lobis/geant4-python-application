"""Python adaptation of extended/medical/GammaTherapy dose scoring."""
from __future__ import annotations
import argparse
from pathlib import Path
import awkward as ak
import geant4_python_application as g4

GDML='''<gdml><solids><box name="W" x="400" y="400" z="1000" lunit="mm"/><box name="T" x="60" y="60" z="10" lunit="mm"/><box name="P" x="300" y="300" z="400" lunit="mm"/><box name="C" x="300" y="300" z="1" lunit="mm"/></solids><structure><volume name="TLV"><materialref ref="G4_W"/><solidref ref="T"/></volume><volume name="PLV"><materialref ref="G4_WATER"/><solidref ref="P"/></volume><volume name="CLV"><materialref ref="G4_AIR"/><solidref ref="C"/></volume><volume name="World"><materialref ref="G4_AIR"/><solidref ref="W"/><physvol name="Target"><volumeref ref="TLV"/><position unit="mm" x="0" y="0" z="-300"/></physvol><physvol name="CheckVolume"><volumeref ref="CLV"/><position unit="mm" x="0" y="0" z="-201"/></physvol><physvol name="Phantom"><volumeref ref="PLV"/><position unit="mm" x="0" y="0" z="0"/></physvol></volume></structure><setup name="Default" version="1"><world ref="World"/></setup></gdml>'''

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("-n","--events",type=int,default=100); p.add_argument("--batch",action="store_true"); p.add_argument("-o","--output",type=Path,default=Path("gamma_therapy_mesh.csv")); a=p.parse_args()
 with g4.Application(gdml=GDML,physics="FTFP_BERT",seed=137) as app:
  mesh=g4.NativeScoringMesh(app,"phantomMesh","doseEnergy").box((150,150,200),(10,10,20),center=(0,0,0))
  app.commands(["/gun/particle gamma","/gun/energy 6 MeV","/gun/position 0 0 -45 cm","/gun/direction 0 0 1"])
  if not a.batch: app.visualize(); return
  events=app.run(a.events); mesh.dump(a.output)
 dose=float(ak.sum(events.track.step.energy[events.track.step.volume=="Phantom"]))
 print(f"events: {len(events)}, phantom deposited energy: {dose:.3f} keV; mesh: {a.output}")
if __name__=="__main__": main()
