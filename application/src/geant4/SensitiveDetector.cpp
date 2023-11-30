
#include "geant4/SensitiveDetector.h"

using namespace std;
using namespace geant4_app;

SensitiveDetector::SensitiveDetector(const string& name) : G4VSensitiveDetector(name) {}

G4bool SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*) { return true; }

void SensitiveDetector::Initialize(G4HCofThisEvent*) {}
