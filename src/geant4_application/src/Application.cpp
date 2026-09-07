
#include "geant4_application/Application.h"
#include "geant4_application/ActionInitialization.h"
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/PhysicsList.h"
#include "geant4_application/RunAction.h"
#include "geant4_application/SteppingVerbose.h"

#include <G4RunManager.hh>
#include <G4RunManagerFactory.hh>
#include <G4PhysListFactory.hh>
#include <G4OpticalPhysics.hh>
#include <G4EmExtraPhysics.hh>
#include <G4EmDNAPhysics.hh>
#include <G4EmDNAPhysics_option1.hh>
#include <G4EmDNAPhysics_option2.hh>
#include <G4EmDNAPhysics_option3.hh>
#include <G4EmDNAPhysics_option4.hh>
#include <G4EmDNAPhysics_option5.hh>
#include <G4EmDNAPhysics_option6.hh>
#include <G4EmDNAPhysics_option7.hh>
#include <G4EmDNAPhysics_option8.hh>
#include <G4EmDNAChemistry.hh>
#include <G4EmDNAChemistry_option1.hh>
#include <G4EmDNAChemistry_option2.hh>
#include <G4EmDNAChemistry_option3.hh>
#include <G4RadioactiveDecayPhysics.hh>
#include <G4DecayPhysics.hh>
#include <G4VModularPhysicsList.hh>

#ifdef GEANT4_PYTHON_APPLICATION_VISUALIZATION
#include <G4UIExecutive.hh>
#include <G4VisExecutive.hh>
#endif

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

void Application::SetupPhysics(const string& physicsListName, bool optical) {
    if (G4RunManager::GetRunManager() == nullptr) {
        throw runtime_error("The run manager needs to be set up before the physics list");
    }

    if (runManager->GetUserPhysicsList() != nullptr) {
        throw runtime_error("Physics list can only be set up once");
    }

    delete runManager->GetUserPhysicsList();
    G4VUserPhysicsList* physics = nullptr;
    if (physicsListName.empty() || physicsListName == "custom") {
        physics = new PhysicsList(optical);
    } else {
        G4PhysListFactory factory;
        if (!factory.IsReferencePhysList(physicsListName)) {
            throw runtime_error("Unknown Geant4 reference physics list: " + physicsListName);
        }
        physics = factory.GetReferencePhysList(physicsListName);
        if (optical) {
            auto modular = dynamic_cast<G4VModularPhysicsList*>(physics);
            if (modular == nullptr) {
                delete physics;
                throw runtime_error("Optical physics requires a modular physics list");
            }
            modular->RegisterPhysics(new G4OpticalPhysics());
        }
    }
    physics->SetVerboseLevel(0);
    runManager->SetUserInitialization(physics);
}

vector<string> Application::GetAvailablePhysicsLists() {
    G4PhysListFactory factory;
    const auto available = factory.AvailablePhysLists();
    vector<string> names = {"custom"};
    names.reserve(available.size() + 1);
    for (const auto& name: available) {
        names.emplace_back(name.c_str());
    }
    return names;
}

static G4VPhysicsConstructor* CreateExtraPhysics(const string& name) {
    if (name == "G4OpticalPhysics") return new G4OpticalPhysics();
    if (name == "G4EmExtraPhysics") return new G4EmExtraPhysics();
    if (name == "G4RadioactiveDecayPhysics") return new G4RadioactiveDecayPhysics();
    if (name == "G4DecayPhysics") return new G4DecayPhysics();
    if (name == "G4EmDNAPhysics") return new G4EmDNAPhysics();
    if (name == "G4EmDNAPhysics_option1") return new G4EmDNAPhysics_option1();
    if (name == "G4EmDNAPhysics_option2") return new G4EmDNAPhysics_option2();
    if (name == "G4EmDNAPhysics_option3") return new G4EmDNAPhysics_option3();
    if (name == "G4EmDNAPhysics_option4") return new G4EmDNAPhysics_option4();
    if (name == "G4EmDNAPhysics_option5") return new G4EmDNAPhysics_option5();
    if (name == "G4EmDNAPhysics_option6") return new G4EmDNAPhysics_option6();
    if (name == "G4EmDNAPhysics_option7") return new G4EmDNAPhysics_option7();
    if (name == "G4EmDNAPhysics_option8") return new G4EmDNAPhysics_option8();
    if (name == "G4EmDNAChemistry") return new G4EmDNAChemistry();
    if (name == "G4EmDNAChemistry_option1") return new G4EmDNAChemistry_option1();
    if (name == "G4EmDNAChemistry_option2") return new G4EmDNAChemistry_option2();
    if (name == "G4EmDNAChemistry_option3") return new G4EmDNAChemistry_option3();
    return nullptr;
}

vector<string> Application::GetAvailableExtraPhysics() {
    return {"G4OpticalPhysics", "G4EmExtraPhysics", "G4RadioactiveDecayPhysics", "G4DecayPhysics",
            "G4EmDNAPhysics", "G4EmDNAPhysics_option1", "G4EmDNAPhysics_option2", "G4EmDNAPhysics_option3",
            "G4EmDNAPhysics_option4", "G4EmDNAPhysics_option5", "G4EmDNAPhysics_option6",
            "G4EmDNAPhysics_option7", "G4EmDNAPhysics_option8",
            "G4EmDNAChemistry", "G4EmDNAChemistry_option1", "G4EmDNAChemistry_option2", "G4EmDNAChemistry_option3"};
}

void Application::AddExtraPhysics(const string& constructorName) {
    if (G4RunManager::GetRunManager() == nullptr) {
        throw runtime_error("The run manager needs to be set up before adding physics");
    }
    if (runManager->GetUserPhysicsList() == nullptr) {
        throw runtime_error("Setup physics before adding extra physics constructors");
    }
    if (IsInitialized()) {
        throw runtime_error("Extra physics cannot be added after initialization");
    }
    auto* modular = dynamic_cast<G4VModularPhysicsList*>(const_cast<G4VUserPhysicsList*>(runManager->GetUserPhysicsList()));
    if (modular == nullptr) {
        throw runtime_error("Extra physics requires a modular physics list");
    }
    G4VPhysicsConstructor* ctor = CreateExtraPhysics(constructorName);
    if (ctor == nullptr) {
        throw runtime_error("Unknown extra physics constructor: " + constructorName +
                            ". See available_extra_physics()");
    }
    modular->RegisterPhysics(ctor);
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

#ifndef G4MULTITHREADED
    if (nThreads > 0) {
        throw runtime_error(
                "This Geant4 installation was built without multithreading support; "
                "use n_threads=0");
    }
#endif

    const auto runManagerType = nThreads > 0 ? G4RunManagerType::MTOnly : G4RunManagerType::SerialOnly;
    runManager = unique_ptr<G4RunManager>(G4RunManagerFactory::CreateRunManager(runManagerType));
    if (nThreads > 0) {
        runManager->SetNumberOfThreads((G4int) nThreads);
    }
}

bool Application::MultithreadingAvailable() {
#ifdef G4MULTITHREADED
    return true;
#else
    return false;
#endif
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

    SetupRandomEngine();

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

bool Application::VisualizationAvailable() {
#ifdef GEANT4_PYTHON_APPLICATION_VISUALIZATION
    return true;
#else
    return false;
#endif
}

void Application::StartVisualization(const vector<string>& commands) {
#ifdef GEANT4_PYTHON_APPLICATION_VISUALIZATION
    if (!IsInitialized()) {
        Initialize();
    }

    int argc = 1;
    char applicationName[] = "geant4-python-application";
    char* argv[] = {applicationName, nullptr};

    auto visualization = make_unique<G4VisExecutive>();
    visualization->Initialize();

    auto ui = make_unique<G4UIExecutive>(argc, argv, "qt");
    for (const auto& command: commands) {
        Command(command);
    }
    ui->SessionStart();
#else
    (void) commands;
    throw runtime_error(
            "Visualization support was not built. Reinstall with "
            "-Ccmake.define.GEANT4_PYTHON_APPLICATION_VISUALIZATION=ON using a Geant4 build with Qt/OpenGL.");
#endif
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
        if (eventFieldsComplete.find(field) == eventFieldsComplete.end()) {
            throw runtime_error("Invalid event field: " + field);
        }
    }
    eventFields = fields;
}

unordered_set<string> Application::eventFields = {};
