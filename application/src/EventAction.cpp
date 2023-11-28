
#include "geant4/EventAction.h"

#include "geant4/RunManager.h"
#include <iostream>

using namespace std;

EventAction::EventAction() : G4UserEventAction() {}

void EventAction::BeginOfEventAction(const G4Event* event) {
    cout << "Begin of event " << event->GetEventID() << endl;

    auto runManager = dynamic_cast<RunManager*>(G4RunManager::GetRunManager());
}

void EventAction::EndOfEventAction(const G4Event*) {
    auto runManager = dynamic_cast<RunManager*>(G4RunManager::GetRunManager());
}
