
#include "geant4/EventAction.h"
#include <iostream>

using namespace std;

EventAction::EventAction() : G4UserEventAction() {}

void EventAction::BeginOfEventAction(const G4Event* event) {
    cout << "Begin of event " << event->GetEventID() << endl;
}

void EventAction::EndOfEventAction(const G4Event*) {
}
