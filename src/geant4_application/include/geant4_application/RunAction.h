
#pragma once

#include <G4Run.hh>
#include <G4RunManager.hh>
#include <G4UserRunAction.hh>

#include "geant4_application/Application.h"
#include "geant4_application/DataModel.h"

namespace py = pybind11;

namespace geant4_app {

class RunAction : public G4UserRunAction {
public:
    RunAction();

    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction(const G4Run*) override;

    /// Only one instance of RunAction is created for each thread.
    static data::Builders& GetBuilder();
    static std::unique_ptr<py::list> GetContainer();

private:
    std::unique_ptr<data::Builders> builder = nullptr;
    std::mutex mutex;
    static std::unique_ptr<py::list> container;
    static std::vector<std::unique_ptr<data::Builders>> buildersToSnapshot;
};

}// namespace geant4_app
