
#include "geant4_application/SensitiveDetector.h"
#include "geant4_application/EventAction.h"

using namespace std;
using namespace geant4_app;

SensitiveDetector::SensitiveDetector(const string& name) : G4VSensitiveDetector(name) {}

G4bool SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*) {
    EventAction::sensitiveEnergy += step->GetTotalEnergyDeposit() / CLHEP::keV;
    return true;
}

void SensitiveDetector::Initialize(G4HCofThisEvent*) {}
