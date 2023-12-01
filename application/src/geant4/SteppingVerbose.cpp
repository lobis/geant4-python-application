
#include "geant4/SteppingVerbose.h"
#include "geant4/DataModel.h"
#include "geant4/RunAction.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

SteppingVerbose::SteppingVerbose() : G4SteppingVerbose() {}

void SteppingVerbose::TrackingStarted() {
    CopyState();
    if (fStep->GetTrack()->GetCurrentStepNumber() != 0) {
        throw runtime_error("SteppingVerbose::TrackingStarted: fStep->GetTrack()->GetCurrentStepNumber() != 0");
    }
    data::InsertStep(fStep, RunAction::GetBuilder());
}

void SteppingVerbose::StepInfo() {}

void SteppingVerbose::Initialize() {
    auto manager = fManager;
    if (manager == nullptr) {
        throw runtime_error("SteppingVerbose::Initialize: fManager is nullptr");
    }
    fManager->SetVerboseLevel(1);
}
