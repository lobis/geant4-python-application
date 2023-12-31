
#include "geant4_application/EventAction.h"
#include "geant4_application/DataModel.h"
#include "geant4_application/RunAction.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

EventAction::EventAction() : G4UserEventAction() {}

void EventAction::BeginOfEventAction(const G4Event* event) {
    data::InsertEventBegin(event, RunAction::GetBuilder());
    data::InsertEvent(event, RunAction::GetBuilder());
}

void EventAction::EndOfEventAction(const G4Event* event) {
    data::InsertEventEnd(event, RunAction::GetBuilder());
}
