
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

RunAction::RunAction() : G4UserRunAction() {}

void RunAction::BeginOfRunAction(const G4Run*) {
    builder.clear();

    auto steppingVerbose = ((SteppingVerbose*) G4VSteppingVerbose::GetInstance());
    steppingVerbose->Initialize();

    if (IsMaster()) {
        events = make_unique<std::vector<py::object>>();
    }
}

void RunAction::EndOfRunAction(const G4Run*) {
    string error;
    if (!builder.is_valid(error)) {
        throw runtime_error("Builder is not valid: " + error);
    }

    if (!isMaster || !G4Threading::IsMultithreadedApplication()) {
        lock_guard<std::mutex> lock(mutex);
        buildersToSnapshot.push_back(&builder);
    }

    if (isMaster) {
        // snapshot not working on worker threads, why?
        py::gil_scoped_acquire acquire;
        for (auto& builderToSnapshot: buildersToSnapshot) {
            events->push_back(data::SnapshotBuilder(*builderToSnapshot));
            builderToSnapshot->clear();
        }
        buildersToSnapshot.clear();
    }
}

data::Builder& RunAction::GetBuilder() {
    auto runAction = dynamic_cast<RunAction*>(const_cast<G4UserRunAction*>(G4RunManager::GetRunManager()->GetUserRunAction()));
    return runAction->builder;
}

unique_ptr<std::vector<py::object>> RunAction::events = nullptr;

vector<py::object> RunAction::GetEvents() {
    // how to avoid this copy?
    py::gil_scoped_acquire acquire;
    return *std::move(RunAction::events);
}

vector<data::Builder*> RunAction::buildersToSnapshot = {};
