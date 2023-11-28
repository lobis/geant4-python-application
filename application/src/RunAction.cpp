
#include "geant4/RunAction.h"

using namespace std;

RunAction::RunAction() : G4UserRunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {}

void RunAction::EndOfRunAction(const G4Run*) {}
