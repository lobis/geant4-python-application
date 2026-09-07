
#pragma once

#include <G4RunManager.hh>
#include <G4UImanager.hh>

#include "pybind11/chrono.h"
#include "pybind11/complex.h"
#include "pybind11/functional.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "geant4_application/ActionInitialization.h"
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/PhysicsList.h"
#include "geant4_application/PrimaryGeneratorAction.h"
#include "geant4_application/StackingAction.h"

#include <filesystem>

namespace py = pybind11;

namespace geant4_app {

class Application {
private:
    std::unique_ptr<G4RunManager> runManager = nullptr;
    bool isInitialized = false;

    long randomSeed = 0;

    static Application* pInstance;
    void SetupRandomEngine();

    static std::unordered_set<std::string> eventFieldsComplete;
    static std::unordered_set<std::string> eventFields;

public:
    Application();
    ~Application();

    Application(const Application&) = delete;
    Application& operator=(const Application&) = delete;

    void SetRandomSeed(long seed);
    void SetupManager(unsigned short nThreads);
    static bool MultithreadingAvailable();
    void SetupDetector(const std::string& gdml);
    void SetupPhysics(const std::string& physicsListName = "custom", bool optical = false);
    static std::vector<std::string> GetAvailablePhysicsLists();
    void AddExtraPhysics(const std::string& constructorName);
    static std::vector<std::string> GetAvailableExtraPhysics();
    void SetupAction();

    void Initialize();
    py::list Run(const py::object& primaries);
    void StartVisualization(const std::vector<std::string>& commands);
    static bool VisualizationAvailable();

    bool IsSetup() const;
    bool IsInitialized() const;

    inline static std::unordered_set<std::string> GetEventFieldsComplete() { return eventFieldsComplete; }
    inline static std::unordered_set<std::string> GetEventFields() { return eventFields; }
    static void SetEventFields(const std::unordered_set<std::string>& fields);
    inline long GetRandomSeed() const { return randomSeed; }

    static void Command(const std::string& command);
    static void ListCommands(const std::string& directory);
    static G4UImanager* GetUIManager();

    const PrimaryGeneratorAction& GetPrimaryGeneratorAction() const;
    const StackingAction& GetStackingAction() const;
    const DetectorConstruction& GetDetectorConstruction() const;

    static std::filesystem::path GetTemporaryApplicationDirectory();
};

}// namespace geant4_app
