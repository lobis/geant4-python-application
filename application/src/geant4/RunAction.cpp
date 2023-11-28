
#include "geant4/RunAction.h"
#include <G4Threading.hh>
#include <iostream>

using namespace std;

RunAction::RunAction() : G4UserRunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {
    cout << "Begin of run for thread " << G4Threading::G4GetThreadId() << endl;
}

void RunAction::EndOfRunAction(const G4Run*) {
    G4cout << "END OF RUN" << G4endl;
}
