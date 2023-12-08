
#pragma once

#include <G4RunManager.hh>
#include <G4UserRunAction.hh>

#include "geant4_application/DataModel.h"

namespace py = pybind11;

namespace geant4_app {

class RunAction : public G4UserRunAction {
public:
    RunAction();

    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction(const G4Run*) override;

    /// Only one instance of RunAction is created for each thread.
    static data::Builder& GetBuilder();
    static std::vector<py::object>& GetEventCollection();

private:
    data::Builder builder = data::MakeBuilder();
    std::mutex mutex;
    static std::vector<py::object> awkwardArrays;
    static std::vector<data::Builder*> toSnapshot;
};

}// namespace geant4_app
