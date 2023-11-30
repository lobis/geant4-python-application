
#include "geant4/SteppingVerbose.h"
#include "geant4/DataModel.h"
#include "geant4/RunAction.h"

#include <iostream>

using namespace std;

SteppingVerbose::SteppingVerbose() : G4SteppingVerbose() {
    cout << "SteppingVerbose::SteppingVerbose" << endl;
    fManager->SetVerboseLevel(1);
}

void SteppingVerbose::TrackingStarted() {
    CopyState();
    cout << "SteppingVerbose::TrackingStarted" << endl;
    geant4::data::InsertStep(fStep, RunAction::GetBuilder());
}

void SteppingVerbose::StepInfo() {}
