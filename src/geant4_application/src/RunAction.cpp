
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

RunAction::RunAction() : G4UserRunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {
    builder.clear();

    if (IsMaster()) {
        awkwardArrays.clear();
    } else {
        // Worker
    }
}

void RunAction::EndOfRunAction(const G4Run*) {
    string error;
    if (!builder.is_valid(error)) {
        throw std::runtime_error("Builder is not valid: " + error);
    }

    if (!isMaster || !G4Threading::IsMultithreadedApplication()) {
        std::lock_guard<std::mutex> lock(mutex);
        toSnapshot.push_back(&builder);
    }

    if (isMaster) {
        // snapshot not working on worker threads, why?
        for (auto& builderToSnapshot: toSnapshot) {
            awkwardArrays.push_back(data::SnapshotBuilder(*builderToSnapshot));
            builderToSnapshot->clear();
        }
        toSnapshot.clear();
    }
}

data::Builder& RunAction::GetBuilder() {
    auto runAction = dynamic_cast<RunAction*>(const_cast<G4UserRunAction*>(G4RunManager::GetRunManager()->GetUserRunAction()));
    return runAction->builder;
}

std::vector<py::object> RunAction::awkwardArrays = {};

std::vector<py::object>& RunAction::GetEventCollection() {
    auto runAction = dynamic_cast<RunAction*>(const_cast<G4UserRunAction*>(G4RunManager::GetRunManager()->GetUserRunAction()));
    return runAction->awkwardArrays;
}

std::vector<data::Builder*> RunAction::toSnapshot = {};
