
#include "geant4/RunAction.h"
#include "geant4/SteppingVerbose.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

RunAction::RunAction() : G4UserRunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {
    builder.clear();

    auto steppingVerbose = ((SteppingVerbose*) G4VSteppingVerbose::GetInstance());
    if (steppingVerbose == nullptr) {
        throw std::runtime_error("SteppingVerbose is nullptr");
    }
    steppingVerbose->Initialize();

    if (IsMaster()) {
        builderMainPtr = &builder;
    } else {
        // Worker
    }
}

void RunAction::EndOfRunAction(const G4Run*) {
    string error;
    if (!builder.is_valid(error)) {
        throw std::runtime_error("Builder is not valid: " + error);
    }

    if (IsMaster()) {
    } else {
        // move the data into the main thread builder
        std::lock_guard<std::mutex> lock(mutex);
        auto& builderMain = *builderMainPtr;
        // TODO: implement
    }
}

data::Builder& RunAction::GetBuilder() {
    auto runAction = dynamic_cast<RunAction*>(const_cast<G4UserRunAction*>(G4RunManager::GetRunManager()->GetUserRunAction()));
    return runAction->builder;
}

data::Builder* RunAction::builderMainPtr = nullptr;
