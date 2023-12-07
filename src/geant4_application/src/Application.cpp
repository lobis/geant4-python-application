
#include "geant4_application/Application.h"
#include "geant4_application/ActionInitialization.h"
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/PhysicsList.h"
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

#include <G4RunManager.hh>
#include <G4RunManagerFactory.hh>

#include <random>

using namespace std;
using namespace geant4_app;
namespace py = pybind11;

Application* Application::pInstance = nullptr;

Application::Application() {
    // only a single Application can ever be created (geant4 limitation)
    if (pInstance != nullptr) {
        throw runtime_error("Application can only be created once");
    }
    pInstance = this;
}

/// We cannot clean up everything, creating a new application will fail after initializing the kernel, so we don't allow it.
/// We don't want to clear the pointer, this would suggest it's okay to create a new application.
Application::~Application() = default;

void Application::SetupRandomEngine() {
    CLHEP::HepRandom::setTheEngine(new CLHEP::RanecuEngine);
    if (randomSeed == 0) {
        randomSeed = std::random_device()();
    }
    CLHEP::HepRandom::setTheSeed(randomSeed);
}

void Application::SetupDetector(const string& gdml) {
    if (G4RunManager::GetRunManager() == nullptr) {
        throw runtime_error("The run manager needs to be set up before the detector");
    }

    delete runManager->GetUserDetectorConstruction();
    runManager->SetUserInitialization(new DetectorConstruction(gdml));
}

void Application::SetupPhysics() {
    if (G4RunManager::GetRunManager() == nullptr) {
        throw runtime_error("The run manager needs to be set up before the physics list");
    }

    if (runManager->GetUserPhysicsList() != nullptr) {
        throw runtime_error("Physics list can only be set up once");
    }

    runManager->SetUserInitialization(new PhysicsList());
}

void Application::SetupAction() {
    if (G4RunManager::GetRunManager() == nullptr) {
        throw runtime_error("The run manager needs to be set up before the action initialization");
    }

    if (runManager->GetUserDetectorConstruction() == nullptr) {
        throw runtime_error("The detector needs to be set up before the action initialization");
    }

    if (runManager->GetUserPhysicsList() == nullptr) {
        throw runtime_error("The physics list to be set up before the action initialization");
    }

    delete runManager->GetUserActionInitialization();
    delete G4VSteppingVerbose::GetInstance();
    runManager->SetUserInitialization(new ActionInitialization());
}

void Application::SetupManager(unsigned short nThreads) {
    if (G4RunManager::GetRunManager() != nullptr) {
        throw runtime_error("The run manager can only be set up once");
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

    if (IsInitialized()) {
        throw runtime_error("Application is already initialized");
    }

    SetupRandomEngine();

    runManager->Initialize();
    isInitialized = true;
}

py::object Application::Run(int nEvents) {
    if (!IsInitialized()) {
        throw runtime_error("Application needs to be initialized first");
    }
    runManager->BeamOn(nEvents);

    auto& builder = RunAction::GetBuilder();
    const auto events = data::SnapshotBuilder(builder);
    builder.clear();
    return events;
}

bool Application::IsSetup() const {
    return runManager != nullptr && runManager->GetUserDetectorConstruction() != nullptr &&
           runManager->GetUserPhysicsList() != nullptr && runManager->GetUserActionInitialization() != nullptr;
}

bool Application::IsInitialized() const {
    return runManager != nullptr && isInitialized;
}

void Application::SetRandomSeed(long seed) {
    randomSeed = seed;
}

G4UImanager* Application::GetUIManager() {
    auto ui = G4UImanager::GetUIpointer();
    if (ui == nullptr) {
        throw runtime_error("The UI manager is not available");
    }
    return ui;
}

void Application::Command(const string& command) {
    auto ui = GetUIManager();
    int code = ui->ApplyCommand(command);
    if (code != 0) {
        throw runtime_error("Command '" + command + "' failed with code " + to_string(code));
    }
}

void Application::ListCommands(const string& directory) {
    auto ui = GetUIManager();
    ui->ListCommands(directory.c_str());
}

const PrimaryGeneratorAction& Application::GetPrimaryGeneratorAction() const {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }
    const auto primaryGeneratorAction = dynamic_cast<const PrimaryGeneratorAction*>(runManager->GetUserPrimaryGeneratorAction());
    if (primaryGeneratorAction == nullptr) {
        throw runtime_error("Primary generator action is not available");
    }
    return *primaryGeneratorAction;
}

const StackingAction& Application::GetStackingAction() const {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }
    const auto stackingAction = dynamic_cast<const StackingAction*>(runManager->GetUserStackingAction());
    if (stackingAction == nullptr) {
        throw runtime_error("Stacking action is not available");
    }
    return *stackingAction;
}

const DetectorConstruction& Application::GetDetectorConstruction() const {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }
    const auto detectorConstruction = dynamic_cast<const DetectorConstruction*>(runManager->GetUserDetectorConstruction());
    if (detectorConstruction == nullptr) {
        throw runtime_error("Detector construction is not available");
    }
    return *detectorConstruction;
}
