
#include "geant4/EventAction.h"
#include "geant4/DataModel.h"
#include "geant4/RunAction.h"

#include <iostream>

using namespace std;

EventAction::EventAction() : G4UserEventAction() {}

void EventAction::BeginOfEventAction(const G4Event* event) {
    geant4::data::InsertEventBegin(event, RunAction::GetBuilder());
}

void EventAction::EndOfEventAction(const G4Event* event) {
    geant4::data::InsertEventEnd(event, RunAction::GetBuilder());
}
