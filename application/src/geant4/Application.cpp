
#include "geant4/Application.h"
#include "geant4/ActionInitialization.h"
#include "geant4/DetectorConstruction.h"
#include "geant4/PhysicsList.h"

#include <G4RunManagerFactory.hh>

#include <iostream>

using namespace std;
using namespace geant4;

Application::Application() = default;

template<typename... Args>
void Application::SetupDetector(Args... arg) {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }

    if (runManager->GetUserDetectorConstruction() != nullptr) {
        throw runtime_error("Detector is already set up");
    }

    runManager->SetUserInitialization(new DetectorConstruction(std::forward<Args>(arg)...));
}

// explicit template instantiation
template void Application::SetupDetector<string, set<string>>(string, set<string>);
template void Application::SetupDetector<string>(string);

void Application::SetupPhysics() {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }

    if (runManager->GetUserPhysicsList() != nullptr) {
        throw runtime_error("Physics is already set up");
    }

    runManager->SetUserInitialization(new PhysicsList());
}

void Application::SetupAction() {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }

    // check detector and physics are set up
    if (runManager->GetUserDetectorConstruction() == nullptr) {
        throw runtime_error("Detector needs to be set up first");
    }

    if (runManager->GetUserPhysicsList() == nullptr) {
        throw runtime_error("Physics needs to be set up first");
    }

    if (runManager->GetUserActionInitialization() != nullptr) {
        throw runtime_error("Action is already set up");
    }

    runManager->SetUserInitialization(new ActionInitialization());
}

void Application::SetupManager(unsigned short nThreads) {
    if (runManager != nullptr) {
        throw runtime_error("RunManager is already set up");
    }
    const auto runManagerType = nThreads > 0 ? G4RunManagerType::MTOnly : G4RunManagerType::SerialOnly;
    runManager = unique_ptr<G4RunManager>(G4RunManagerFactory::CreateRunManager(runManagerType));
    if (nThreads > 0) {
        runManager->SetNumberOfThreads((G4int) nThreads);
    }
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
    return runManager != nullptr && runManager->GetUserDetectorConstruction() != nullptr &&
           runManager->GetUserPhysicsList() != nullptr && runManager->GetUserActionInitialization() != nullptr;
}

bool Application::IsInitialized() const {
    return runManager != nullptr && isInitialized;
}
