
#include "geant4_application/ActionInitialization.h"
#include "geant4_application/EventAction.h"
#include "geant4_application/PrimaryGeneratorAction.h"
#include "geant4_application/RunAction.h"
#include "geant4_application/StackingAction.h"
#include "geant4_application/SteppingAction.h"
#include "geant4_application/SteppingVerbose.h"
#include "geant4_application/TrackingAction.h"

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

    // G4EventManager::GetEventManager()->SetNumberOfAdditionalWaitingStacks(1);  // optical stack
}

G4VSteppingVerbose* ActionInitialization::InitializeSteppingVerbose() const {
    return new SteppingVerbose;
}
