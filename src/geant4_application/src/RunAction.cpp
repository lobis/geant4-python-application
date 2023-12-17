
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

#include <iostream>

using namespace std;
using namespace geant4_app;

RunAction::RunAction() : G4UserRunAction() {}

void RunAction::BeginOfRunAction(const G4Run* run) {
    lock_guard<std::mutex> lock(mutex);

    builder = make_unique<data::Builders>(Application::GetEventFields());

    auto steppingVerbose = ((SteppingVerbose*) G4VSteppingVerbose::GetInstance());
    steppingVerbose->Initialize();

    if (IsMaster()) {
        container = make_unique<vector<py::object>>();
    }

    cout << "RUN ID: " << run->GetRunID() << " RANDOM SEED: " << G4Random::getTheSeed() << endl;
}

void RunAction::EndOfRunAction(const G4Run*) {
    lock_guard<std::mutex> lock(mutex);

    if (!isMaster || !G4Threading::IsMultithreadedApplication()) {
        buildersToSnapshot.push_back(std::move(builder));
    }

    if (isMaster) {
        for (auto& builders: buildersToSnapshot) {
            container->push_back(BuilderToObject(std::move(builders)));
        }
        buildersToSnapshot.clear();
    }
}

data::Builders& RunAction::GetBuilder() {
    auto runAction = dynamic_cast<RunAction*>(const_cast<G4UserRunAction*>(G4RunManager::GetRunManager()->GetUserRunAction()));
    return *runAction->builder;
}

unique_ptr<vector<py::object>> RunAction::container = nullptr;

unique_ptr<vector<py::object>> RunAction::GetContainer() {
    return std::move(RunAction::container);
}

vector<std::unique_ptr<data::Builders>> RunAction::buildersToSnapshot = {};
