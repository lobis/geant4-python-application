
#include "geant4/SteppingAction.h"

#include <G4Step.hh>
#include <iostream>

#include "geant4/RunManager.h"

using namespace std;

SteppingAction::SteppingAction() : G4UserSteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    auto runManager = dynamic_cast<RunManager*>(G4RunManager::GetRunManager());
}
