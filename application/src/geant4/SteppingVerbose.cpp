
#include "geant4/SteppingVerbose.h"
#include "geant4/DataModel.h"
#include "geant4/RunAction.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

SteppingVerbose::SteppingVerbose() : G4SteppingVerbose() {
    cout << "SteppingVerbose::SteppingVerbose" << endl;
    fManager->SetVerboseLevel(1);
}

void SteppingVerbose::TrackingStarted() {
    CopyState();
    cout << "SteppingVerbose::TrackingStarted" << endl;
    data::InsertStep(fStep, RunAction::GetBuilder());
}

void SteppingVerbose::StepInfo() {}
