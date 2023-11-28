//
// Created by Luis Antonio Obis Aparicio on 28/11/23.
//

#include "geant4/ActionInitialization.h"
#include "geant4/EventAction.h"
#include "geant4/PrimaryGeneratorAction.h"
#include "geant4/RunAction.h"
#include "geant4/StackingAction.h"
#include "geant4/SteppingAction.h"
#include "geant4/TrackingAction.h"

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
