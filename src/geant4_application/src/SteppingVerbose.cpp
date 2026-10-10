
#include "geant4_application/SteppingVerbose.h"
#include "geant4_application/DataModel.h"
#include "geant4_application/RunAction.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

SteppingVerbose::SteppingVerbose() : G4SteppingVerbose() {}

void SteppingVerbose::TrackingStarted() {
    CopyState();
    // Optical stacking (scintillation/Cerenkov) can invoke TrackingStarted
    // with CurrentStepNumber != 0 for resumed tracks; skip duplicate init
    // record instead of aborting the run.
    if (fStep->GetTrack()->GetCurrentStepNumber() != 0) {
        return;
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
