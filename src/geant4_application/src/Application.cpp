
#include "geant4_application/Application.h"
#include "geant4_application/ActionInitialization.h"
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/PhysicsList.h"
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

// TODO: conditional include
#include <G4UIExecutive.hh>
#include <G4VisExecutive.hh>
#include <G4VisManager.hh>
// TODO: conditional include

#include <G4RunManager.hh>
#include <G4RunManagerFactory.hh>

#include <random>

using namespace std;
using namespace geant4_app;
namespace py = pybind11;

Application* Application::pInstance = nullptr;

Application::Application() {
    // if the instance already exists, return it, otherwise create one
    if (pInstance != nullptr) {
        throw runtime_error("Application can only be created once");
        return;
    }
    if (G4RunManager::GetRunManager() != nullptr) {
        throw runtime_error("RunManager already exists on Application creation");
    }
    pInstance = this;
}

Application::~Application() {
    // Recreating the Application may cause a segfault
    pInstance = nullptr;
}

void Application::SetupRandomEngine() {
    CLHEP::HepRandom::setTheEngine(new CLHEP::RanecuEngine);
    if (randomSeed == 0) {
        randomSeed = std::random_device()();
    }
    CLHEP::HepRandom::setTheSeed(randomSeed);
}

void Application::SetupDetector(string gdml, const set<string>& sensitiveVolumes) {
    if (runManager == nullptr) {
        throw runtime_error("RunManager needs to be set up first");
    }

    if (runManager->GetUserDetectorConstruction() != nullptr) {
        throw runtime_error("Detector is already set up");
    }

    // sensitive volumes should be a set of strings
    set<string> sensitiveVolumesSet;
    for (const auto& volumeName: sensitiveVolumes) {
        sensitiveVolumesSet.insert(volumeName);
    }

    runManager->SetUserInitialization(new DetectorConstruction(std::move(gdml), sensitiveVolumesSet));
}

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
    if (runManager != nullptr || G4RunManager::GetRunManager() != nullptr) {
        throw runtime_error("RunManager is already set up");
    }
    G4VSteppingVerbose::SetInstance(new SteppingVerbose);
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
        throw runtime_error("UI manager is not available");
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
    // mostly to give Python easy access to the static methods
    const auto primaryGeneratorAction = dynamic_cast<const PrimaryGeneratorAction*>(runManager->GetUserPrimaryGeneratorAction());
    if (primaryGeneratorAction == nullptr) {
        throw runtime_error("Primary generator action is not available");
    }
    return *primaryGeneratorAction;
}

const StackingAction& Application::GetStackingAction() const {
    // mostly to give Python easy access to the static methods
    const auto stackingAction = dynamic_cast<const StackingAction*>(runManager->GetUserStackingAction());
    if (stackingAction == nullptr) {
        throw runtime_error("Stacking action is not available");
    }
    return *stackingAction;
}

const DetectorConstruction& Application::GetDetectorConstruction() const {
    // mostly to give Python easy access to the static methods
    const auto detectorConstruction = dynamic_cast<const DetectorConstruction*>(runManager->GetUserDetectorConstruction());
    if (detectorConstruction == nullptr) {
        throw runtime_error("Detector construction is not available");
    }
    return *detectorConstruction;
}

void Application::StartGUI() {
    throw runtime_error("Not working yet ):");

    auto vis = new G4VisExecutive;
    vis->Initialize();
    auto uiExecutive = new G4UIExecutive(1, nullptr);

    // start session
    uiExecutive->SessionStart();
}