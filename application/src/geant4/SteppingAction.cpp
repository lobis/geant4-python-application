
#include "geant4/SteppingAction.h"

#include "geant4/DataModel.h"
#include "geant4/RunAction.h"
#include <G4Step.hh>
#include <iostream>

using namespace std;
using namespace geant4_app;

SteppingAction::SteppingAction() : G4UserSteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    data::InsertStep(step, RunAction::GetBuilder());
}
