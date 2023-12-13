
#include "geant4_application/DataModel.h"
#include "geant4_application/Application.h"

#include <G4HadronicProcess.hh>
#include <G4Nucleus.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTypes.hh>
#include <G4Run.hh>
#include <G4RunManager.hh>
#include <G4UnitsTable.hh>
#include <G4VProcess.hh>
#include <iostream>

#include <pybind11/numpy.h>
#include <pybind11/stl.h>

using namespace std;
using namespace geant4_app;

std::unordered_set<std::string> Application::eventFieldsComplete = {"run_id", "event_id", "track_id", "track_parent_id", "track_initial_energy", "track_initial_time", "track_initial_position_x", "track_initial_position_y", "track_initial_position_z", "step_energy", "step_time", "step_position_x", "step_position_y", "step_position_z"};

namespace geant4_app::data {

void InsertEvent(const G4Event* event, Builders& builders) {
    if (builders.fields.contains("run_id")) {
        builders.run_id.append(G4RunManager::GetRunManager()->GetCurrentRun()->GetRunID());
    }
    if (builders.fields.contains("event_id")) {
        builders.event_id.append(event->GetEventID());
    }
}

void InsertEventBegin(const G4Event* event, Builders& builder) {
    // track fields
    if (builder.fields.contains("track_id")) {
        builder.track_id.begin_list();
    }
    if (builder.fields.contains("track_parent_id")) {
        builder.track_parent_id.begin_list();
    }
    if (builder.fields.contains("track_initial_energy")) {
        builder.track_initial_energy.begin_list();
    }
    if (builder.fields.contains("track_initial_time")) {
        builder.track_initial_time.begin_list();
    }
    if (builder.fields.contains("track_initial_position_x")) {
        builder.track_initial_position_x.begin_list();
    }
    if (builder.fields.contains("track_initial_position_y")) {
        builder.track_initial_position_y.begin_list();
    }
    if (builder.fields.contains("track_initial_position_z")) {
        builder.track_initial_position_z.begin_list();
    }
    // step fields
    if (builder.fields.contains("step_energy")) {
        builder.step_energy.begin_list();
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.begin_list();
    }
    if (builder.fields.contains("step_position_x")) {
        builder.step_position_x.begin_list();
    }
    if (builder.fields.contains("step_position_y")) {
        builder.step_position_y.begin_list();
    }
    if (builder.fields.contains("step_position_z")) {
        builder.step_position_z.begin_list();
    }
}

void InsertEventEnd(const G4Event*, Builders& builder) {
    // track fields
    if (builder.fields.contains("track_id")) {
        builder.track_id.end_list();
    }
    if (builder.fields.contains("track_parent_id")) {
        builder.track_parent_id.end_list();
    }
    if (builder.fields.contains("track_initial_energy")) {
        builder.track_initial_energy.end_list();
    }
    if (builder.fields.contains("track_initial_time")) {
        builder.track_initial_time.end_list();
    }
    if (builder.fields.contains("track_initial_position_x")) {
        builder.track_initial_position_x.end_list();
    }
    if (builder.fields.contains("track_initial_position_y")) {
        builder.track_initial_position_y.end_list();
    }
    if (builder.fields.contains("track_initial_position_z")) {
        builder.track_initial_position_z.end_list();
    }
    // step fields
    if (builder.fields.contains("step_energy")) {
        builder.step_energy.end_list();
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.end_list();
    }
    if (builder.fields.contains("step_position_x")) {
        builder.step_position_x.end_list();
    }
    if (builder.fields.contains("step_position_y")) {
        builder.step_position_y.end_list();
    }
    if (builder.fields.contains("step_position_z")) {
        builder.step_position_z.end_list();
    }
}

void InsertTrack(const G4Track* track, Builders& builder) {
    if (builder.fields.contains("track_id")) {
        builder.track_id.content().append(track->GetTrackID());
    }
    if (builder.fields.contains("track_parent_id")) {
        builder.track_parent_id.content().append(track->GetParentID());
    }
    if (builder.fields.contains("track_initial_energy")) {
        builder.track_initial_energy.content().append(track->GetVertexKineticEnergy() / units::energy);
    }
    if (builder.fields.contains("track_initial_time")) {
        builder.track_initial_time.content().append(track->GetGlobalTime() / units::time);
    }
    if (builder.fields.contains("track_initial_position_x")) {
        builder.track_initial_position_x.content().append(track->GetVertexPosition().x() / units::length);
    }
    if (builder.fields.contains("track_initial_position_y")) {
        builder.track_initial_position_y.content().append(track->GetVertexPosition().y() / units::length);
    }
    if (builder.fields.contains("track_initial_position_z")) {
        builder.track_initial_position_z.content().append(track->GetVertexPosition().z() / units::length);
    }
}

void InsertTrackBegin(const G4Track* track, Builders& builder) {
    if (builder.fields.contains("step_energy")) {
        builder.step_energy.content().begin_list();
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.content().begin_list();
    }
    if (builder.fields.contains("step_position_x")) {
        builder.step_position_x.content().begin_list();
    }
    if (builder.fields.contains("step_position_y")) {
        builder.step_position_y.content().begin_list();
    }
    if (builder.fields.contains("step_position_z")) {
        builder.step_position_z.content().begin_list();
    }
}

void InsertTrackEnd(const G4Track*, Builders& builder) {
    if (builder.fields.contains("step_energy")) {
        builder.step_energy.content().end_list();
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.content().end_list();
    }
    if (builder.fields.contains("step_position_x")) {
        builder.step_position_x.content().end_list();
    }
    if (builder.fields.contains("step_position_y")) {
        builder.step_position_y.content().end_list();
    }
    if (builder.fields.contains("step_position_z")) {
        builder.step_position_z.content().end_list();
    }
}

void InsertStep(const G4Step* step, Builders& builder) {
    const G4Track* track = step->GetTrack();

    const auto& stepPost = step->GetPostStepPoint();
    const auto& stepPre = step->GetPreStepPoint();

    const auto process = step->GetPostStepPoint()->GetProcessDefinedStep();
    G4String processName = "InitStep";
    G4String processTypeName = "InitStep";
    if (track->GetCurrentStepNumber() != 0) {
        // 0 = Init step (G4SteppingVerbose) process is not defined for this step
        processName = process->GetProcessName();
        processTypeName = G4VProcess::GetProcessTypeName(process->GetProcessType());
    }

    if (builder.fields.contains("step_energy")) {
        builder.step_energy.content().content().append(step->GetTotalEnergyDeposit() / units::energy);
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.content().content().append(stepPost->GetGlobalTime() / units::time);
    }
    if (builder.fields.contains("step_position_x")) {
        builder.step_position_x.content().content().append(stepPost->GetPosition().x() / units::length);
    }
    if (builder.fields.contains("step_position_y")) {
        builder.step_position_y.content().content().append(stepPost->GetPosition().y() / units::length);
    }
    if (builder.fields.contains("step_position_z")) {
        builder.step_position_z.content().content().append(stepPost->GetPosition().z() / units::length);
    }
}

template<typename T>
py::object snapshot_builder(const T& builder) {
    // How much memory to allocate?
    std::map<std::string, size_t> names_nbytes = {};
    builder.buffer_nbytes(names_nbytes);

    // Allocate memory
    std::map<std::string, void*> buffers = {};
    for (auto it: names_nbytes) {
        uint8_t* ptr = new uint8_t[it.second];
        buffers[it.first] = (void*) ptr;
    }

    // Write non-contiguous contents to memory
    builder.to_buffers(buffers);
    auto from_buffers = py::module::import("awkward").attr("from_buffers");

    // Build Python dictionary containing arrays
    // dtypes not important here as long as they match the underlying buffer
    // as Awkward Array calls `frombuffer` to convert to the correct type
    py::dict container;
    for (auto it: buffers) {

        // Create capsule that frees the allocated data when out of scope
        py::capsule free_when_done(it.second, [](void* data) {
            uint8_t* dataPtr = reinterpret_cast<uint8_t*>(data);
            delete[] dataPtr;
        });

        // Adopt the memory filled by `to_buffers` as a NumPy array
        // We only need to return a "buffer" here, but py::array_t let's
        // us associate a capsule for destruction, which means that
        // Python can own this memory. Therefore, we use py::array_t
        uint8_t* data = reinterpret_cast<uint8_t*>(it.second);
        container[py::str(it.first)] = py::array_t<uint8_t>(
                {names_nbytes[it.first]},
                {sizeof(uint8_t)},
                data,
                free_when_done);
    }
    return from_buffers(builder.form(), builder.length(), container);
}

py::object SnapshotBuilder(Builders& builder) {
    py::dict snapshot;
    if (builder.fields.contains("run_id")) {
        snapshot["run_id"] = snapshot_builder(builder.run_id);
    }
    if (builder.fields.contains("event_id")) {
        snapshot["event_id"] = snapshot_builder(builder.event_id);
    }
    if (builder.fields.contains("track_id")) {
        snapshot["track_id"] = snapshot_builder(builder.track_id);
    }
    if (builder.fields.contains("track_parent_id")) {
        snapshot["track_parent_id"] = snapshot_builder(builder.track_parent_id);
    }
    if (builder.fields.contains("track_initial_energy")) {
        snapshot["track_initial_energy"] = snapshot_builder(builder.track_initial_energy);
    }
    if (builder.fields.contains("track_initial_time")) {
        snapshot["track_initial_time"] = snapshot_builder(builder.track_initial_time);
    }
    if (builder.fields.contains("track_initial_position_x")) {
        snapshot["track_initial_position_x"] = snapshot_builder(builder.track_initial_position_x);
    }
    if (builder.fields.contains("track_initial_position_y")) {
        snapshot["track_initial_position_y"] = snapshot_builder(builder.track_initial_position_y);
    }
    if (builder.fields.contains("track_initial_position_z")) {
        snapshot["track_initial_position_z"] = snapshot_builder(builder.track_initial_position_z);
    }
    if (builder.fields.contains("step_energy")) {
        snapshot["step_energy"] = snapshot_builder(builder.step_energy);
    }
    if (builder.fields.contains("step_time")) {
        snapshot["step_time"] = snapshot_builder(builder.step_time);
    }
    if (builder.fields.contains("step_position_x")) {
        snapshot["step_position_x"] = snapshot_builder(builder.step_position_x);
    }
    if (builder.fields.contains("step_position_y")) {
        snapshot["step_position_y"] = snapshot_builder(builder.step_position_y);
    }
    if (builder.fields.contains("step_position_z")) {
        snapshot["step_position_z"] = snapshot_builder(builder.step_position_z);
    }
    return snapshot;
}

}// namespace geant4_app::data
