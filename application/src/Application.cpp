
#include "geant4/Application.h"

#include <G4RunManagerFactory.hh>

#include <iostream>

using namespace std;
using namespace geant4;

Application::Application() {}

void Application::Setup() {
    if (IsSetup()) {
        // Geant4 RunManager cannot be constructed twice
        throw runtime_error("Application is already set up");
    }
    const auto runManagerType = G4RunManagerType::SerialOnly;
    runManager = unique_ptr<G4RunManager>(G4RunManagerFactory::CreateRunManager(runManagerType));

    // runManager will manage the lifetime of the following objects
    runManager->SetUserInitialization(new DetectorConstruction());
    runManager->SetUserInitialization(new PhysicsList());

    runManager->SetUserAction(new PrimaryGeneratorAction());
    runManager->SetUserAction(new SteppingAction());
    runManager->SetUserAction(new TrackingAction());
    runManager->SetUserAction(new EventAction());
}

void Application::Initialize() {
    if (!IsSetup()) {
        throw runtime_error("Application needs to be set up first");
    }
    runManager->Initialize();
    isInitialized = true;
}

void Application::Run(int nEvents) {
    if (!IsInitialized()) {
        throw runtime_error("Application needs to be initialized first");
    }
    runManager->BeamOn(nEvents);
}

bool Application::IsSetup() const {
    return runManager != nullptr;
}

bool Application::IsInitialized() const {
    return runManager != nullptr && isInitialized;
}
