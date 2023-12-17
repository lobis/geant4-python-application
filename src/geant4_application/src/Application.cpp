
#include "geant4_application/Application.h"
#include "geant4_application/ActionInitialization.h"
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/PhysicsList.h"
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

#include <G4RunManager.hh>
#include <G4RunManagerFactory.hh>

#include <algorithm>
#include <random>
#include <unordered_set>

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
    G4Random::setTheEngine(new CLHEP::RanecuEngine);
    if (randomSeed == 0) {
        randomSeed = std::random_device()();
    }
    G4Random::setTheSeed(randomSeed);
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

    delete runManager->GetUserPhysicsList();
    auto physics = new PhysicsList();
    physics->SetVerboseLevel(0);
    runManager->SetUserInitialization(physics);
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
    runManager->SetUserInitialization(new ActionInitialization());
}

void Application::SetupManager(unsigned short nThreads) {
    if (G4RunManager::GetRunManager() != nullptr) {
        throw runtime_error("The run manager can only be set up once");
    }

    delete G4VSteppingVerbose::GetInstance();
    SteppingVerbose::SetInstance(new SteppingVerbose);

    // https://geant4-forum.web.cern.ch/t/different-random-seeds-but-same-results/324/5
    // seed needs to be setup before the run manager is created
    SetupRandomEngine();

    const auto runManagerType = nThreads > 0 ? G4RunManagerType::MTOnly : G4RunManagerType::SerialOnly;
    runManager = unique_ptr<G4RunManager>(G4RunManagerFactory::CreateRunManager(runManagerType));
    if (nThreads > 0) {
        runManager->SetNumberOfThreads((G4int) nThreads);
    }
}

void Application::Initialize() {
    if (runManager != nullptr && runManager->GetUserDetectorConstruction() != nullptr &&
        runManager->GetUserPhysicsList() != nullptr && runManager->GetUserActionInitialization() == nullptr) {
        // automatically set up the action initialization if it hasn't been set up yet
        SetupAction();
    }

    if (!IsSetup()) {
        throw runtime_error("Application needs to be set up first");
    }

    if (IsInitialized()) {
        throw runtime_error("Application is already initialized");
    }

    runManager->Initialize();
    isInitialized = true;
}

py::list Application::Run(const py::object& primaries) {
    if (!IsInitialized()) {
        Initialize();
    }
    if (eventFields.empty()) {
        throw runtime_error("Event fields cannot be empty");
    }
    PrimaryGeneratorAction::ClearAwkwardPrimaries();

    // check if it's a python integer
    if (primaries.ptr()->ob_type == &PyLong_Type) {
        auto nEvents = py::cast<G4int>(primaries);
        if (nEvents < 0) {
            throw runtime_error("Number of events cannot be negative");
        }
        runManager->BeamOn(nEvents);
        return *RunAction::GetContainer();
    }
    // check if it is an awkward array
    else {
        py::object ak = py::module::import("awkward");
        py::object ak_array = ak.attr("Array");
        if (!py::isinstance(primaries, ak_array)) {
            throw runtime_error("primaries must be an integer or an awkward array");
        }
        py::object len_func = py::module::import("builtins").attr("len");
        const auto fields = py::cast<py::set>(primaries.attr("fields"));
        const auto nEvents = py::cast<G4int>(len_func(primaries));

        if (fields.contains("energy")) {
            std::vector<double> energies = py::cast<std::vector<double>>(primaries.attr("energy"));
            PrimaryGeneratorAction::SetAwkwardPrimaryEnergies(energies);
        }
        if (fields.contains("particle")) {
            std::vector<std::string> particles = py::cast<std::vector<std::string>>(primaries.attr("particle"));
            PrimaryGeneratorAction::SetAwkwardPrimaryParticles(particles);
        }
        if (fields.contains("position")) {
            std::vector<double> positionX = py::cast<std::vector<double>>(primaries.attr("position")["x"]);
            std::vector<double> positionY = py::cast<std::vector<double>>(primaries.attr("position")["y"]);
            std::vector<double> positionZ = py::cast<std::vector<double>>(primaries.attr("position")["z"]);
            std::vector<std::array<double, 3>> positions;
            for (size_t i = 0; i < nEvents; i++) {
                positions.push_back({positionX[i], positionY[i], positionZ[i]});
            }
            PrimaryGeneratorAction::SetAwkwardPrimaryPositions(positions);
        }
        if (fields.contains("direction")) {
            std::vector<double> directionX = py::cast<std::vector<double>>(primaries.attr("direction")["x"]);
            std::vector<double> directionY = py::cast<std::vector<double>>(primaries.attr("direction")["y"]);
            std::vector<double> directionZ = py::cast<std::vector<double>>(primaries.attr("direction")["z"]);
            std::vector<std::array<double, 3>> directions;
            for (size_t i = 0; i < nEvents; i++) {
                directions.push_back({directionX[i], directionY[i], directionZ[i]});
            }
            PrimaryGeneratorAction::SetAwkwardPrimaryDirections(directions);
        }

        runManager->BeamOn(nEvents);
        return *RunAction::GetContainer();
    }
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

filesystem::path Application::GetTemporaryApplicationDirectory() {
    const auto dir = filesystem::temp_directory_path() / "geant4_python_application";
    if (!filesystem::exists(dir)) {
        filesystem::create_directories(dir);
    }
    return dir;
}

void Application::SetEventFields(const unordered_set<string>& fields) {
    for (const auto& field: fields) {
        if (!eventFieldsComplete.contains(field)) {
            throw runtime_error("Invalid event field: " + field);
        }
    }
    eventFields = fields;
}

unordered_set<string> Application::eventFields = {};
