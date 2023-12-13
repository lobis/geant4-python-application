
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
    static data::Builders& GetBuilder();
    static std::vector<py::object> GetEvents();

private:
    std::unordered_set<std::string> eventFields = {"run_id", "event_id", "track_id", "track_parent_id", "step_energy"};

    data::Builders builder = {eventFields};
    std::mutex mutex;
    static std::unique_ptr<std::vector<py::object>> events;
    static std::vector<data::Builders*> buildersToSnapshot;
};

}// namespace geant4_app
