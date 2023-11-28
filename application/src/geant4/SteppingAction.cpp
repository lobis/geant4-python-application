
#include "geant4/SteppingAction.h"

#include <G4Step.hh>
#include <iostream>

using namespace std;

SteppingAction::SteppingAction() : G4UserSteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
}
