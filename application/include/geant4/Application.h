

#ifndef GEANT4_APPLICATION_H
#define GEANT4_APPLICATION_H

#include <G4RunManager.hh>

#include "pybind11/chrono.h"
#include "pybind11/complex.h"
#include "pybind11/functional.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

namespace geant4 {

class Application {
private:
    std::unique_ptr<G4RunManager> runManager = nullptr;
    bool isInitialized = false;
    long randomSeed = 0;

    static Application* pInstance;
    void SetupRandomEngine();

public:
    Application();
    ~Application();

    Application(const Application&) = delete;
    Application& operator=(const Application&) = delete;

    void SetRandomSeed(long seed);
    void SetupManager(unsigned short nThreads = 0);
    void SetupDetector(std::string gdml, const std::set<std::string>& sensitiveVolumes = {});
    void SetupPhysics();
    void SetupAction();

    void Initialize();
    py::object Run(int nEvents);

    bool IsSetup() const;
    bool IsInitialized() const;

    inline long GetRandomSeed() const { return randomSeed; }

    void Command(const std::string& command);
};

}// namespace geant4

#endif//GEANT4_APPLICATION_H
