
#include "geant4_application/SteppingAction.h"

#include "geant4_application/DataModel.h"
#include "geant4_application/RunAction.h"
#include <G4Step.hh>
#include <iostream>

using namespace std;
using namespace geant4_app;

SteppingAction::SteppingAction() : G4UserSteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    data::InsertStep(step, RunAction::GetBuilder());
}
