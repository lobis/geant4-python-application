
#include "geant4_application/ActionInitialization.h"
#include "geant4_application/EventAction.h"
#include "geant4_application/PrimaryGeneratorAction.h"
#include "geant4_application/RunAction.h"
#include "geant4_application/StackingAction.h"
#include "geant4_application/SteppingAction.h"
#include "geant4_application/SteppingVerbose.h"
#include "geant4_application/TrackingAction.h"

#include <G4EventManager.hh>
#include <G4RunManager.hh>
#include <iostream>

using namespace std;
using namespace geant4_app;

ActionInitialization::ActionInitialization() : G4VUserActionInitialization() {}

void ActionInitialization::BuildForMaster() const {
    SetUserAction(new RunAction);
}

void ActionInitialization::Build() const {
    SetUserAction(new PrimaryGeneratorAction);
    SetUserAction(new RunAction);
    SetUserAction(new EventAction);
    SetUserAction(new SteppingAction);
    SetUserAction(new StackingAction);
    SetUserAction(new TrackingAction);

    // Required for optical photons (scintillation/Cerenkov use an extra stack).
    G4RunManager::GetRunManager()->SetNumberOfAdditionalWaitingStacks(1);
}

G4VSteppingVerbose* ActionInitialization::InitializeSteppingVerbose() const {
    return new SteppingVerbose;
}
