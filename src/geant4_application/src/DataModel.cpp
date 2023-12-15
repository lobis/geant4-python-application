
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

std::unordered_set<std::string> Application::eventFieldsComplete = {
        //
        "id", "run",                                                                                                         //
        "track_id", "track_parent_id", "track_initial_energy", "track_initial_time", "track_weight",                         //
        "track_initial_position_x", "track_initial_position_y", "track_initial_position_z",                                  //
        "track_initial_momentum_x", "track_initial_momentum_y", "track_initial_momentum_z",                                  //
        "track_particle", "track_particle_type", "track_creator_process", "track_creator_process_type", "track_children_ids",//
        "step_energy", "step_time", "step_track_kinetic_energy",                                                             //
        "step_process", "step_process_type",                                                                                 //
        "step_volume", "step_volume_post", "step_nucleus",                                                                   //
        "step_position", "step_momentum"                                                                                     //
};

namespace geant4_app::data {

void InsertEvent(const G4Event* event, Builders& builders) {
    if (builders.fields.contains("run")) {
        builders.run.append(G4RunManager::GetRunManager()->GetCurrentRun()->GetRunID());
    }
    if (builders.fields.contains("id")) {
        builders.id.append(event->GetEventID());
    }
}

void InsertEventBegin(const G4Event* event, Builders& builder) {
    // track fields
    {
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
        if (builder.fields.contains("track_weight")) {
            builder.track_weight.begin_list();
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
        if (builder.fields.contains("track_initial_momentum_x")) {
            builder.track_initial_momentum_x.begin_list();
        }
        if (builder.fields.contains("track_initial_momentum_y")) {
            builder.track_initial_momentum_y.begin_list();
        }
        if (builder.fields.contains("track_initial_momentum_z")) {
            builder.track_initial_momentum_z.begin_list();
        }
        if (builder.fields.contains("track_particle")) {
            builder.track_particle.begin_list();
        }
        if (builder.fields.contains("track_particle_type")) {
            builder.track_particle_type.begin_list();
        }
        if (builder.fields.contains("track_creator_process")) {
            builder.track_creator_process.begin_list();
        }
        if (builder.fields.contains("track_creator_process_type")) {
            builder.track_creator_process_type.begin_list();
        }
        if (builder.fields.contains("track_children_ids")) {
            builder.track_children_ids.begin_list();
        }
    }
    // step fields
    {
        if (builder.fields.contains("step_energy")) {
            builder.step_energy.begin_list();
        }
        if (builder.fields.contains("step_time")) {
            builder.step_time.begin_list();
        }
        if (builder.fields.contains("step_track_kinetic_energy")) {
            builder.step_track_kinetic_energy.begin_list();
        }
        if (builder.fields.contains("step_process")) {
            builder.step_process.begin_list();
        }
        if (builder.fields.contains("step_process_type")) {
            builder.step_process_type.begin_list();
        }
        if (builder.fields.contains("step_volume")) {
            builder.step_volume.begin_list();
        }
        if (builder.fields.contains("step_volume_post")) {
            builder.step_volume_post.begin_list();
        }
        if (builder.fields.contains("step_nucleus")) {
            builder.step_nucleus.begin_list();
        }
        if (builder.fields.contains("step_position")) {
            builder.step_position.content<0>().begin_list();
            builder.step_position.content<1>().begin_list();
            builder.step_position.content<2>().begin_list();
        }
        if (builder.fields.contains("step_momentum")) {
            builder.step_momentum.content<0>().begin_list();
            builder.step_momentum.content<1>().begin_list();
            builder.step_momentum.content<2>().begin_list();
        }
    }
}

void InsertEventEnd(const G4Event*, Builders& builder) {
    // track fields
    {
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
        if (builder.fields.contains("track_weight")) {
            builder.track_weight.end_list();
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
        if (builder.fields.contains("track_initial_momentum_x")) {
            builder.track_initial_momentum_x.end_list();
        }
        if (builder.fields.contains("track_initial_momentum_y")) {
            builder.track_initial_momentum_y.end_list();
        }
        if (builder.fields.contains("track_initial_momentum_z")) {
            builder.track_initial_momentum_z.end_list();
        }
        if (builder.fields.contains("track_particle")) {
            builder.track_particle.end_list();
        }
        if (builder.fields.contains("track_particle_type")) {
            builder.track_particle_type.end_list();
        }
        if (builder.fields.contains("track_creator_process")) {
            builder.track_creator_process.end_list();
        }
        if (builder.fields.contains("track_creator_process_type")) {
            builder.track_creator_process_type.end_list();
        }
        if (builder.fields.contains("track_children_ids")) {
            builder.track_children_ids.end_list();
        }
    }
    // step fields
    {
        if (builder.fields.contains("step_energy")) {
            builder.step_energy.end_list();
        }
        if (builder.fields.contains("step_time")) {
            builder.step_time.end_list();
        }
        if (builder.fields.contains("step_track_kinetic_energy")) {
            builder.step_track_kinetic_energy.end_list();
        }
        if (builder.fields.contains("step_process")) {
            builder.step_process.end_list();
        }
        if (builder.fields.contains("step_process_type")) {
            builder.step_process_type.end_list();
        }
        if (builder.fields.contains("step_volume")) {
            builder.step_volume.end_list();
        }
        if (builder.fields.contains("step_volume_post")) {
            builder.step_volume_post.end_list();
        }
        if (builder.fields.contains("step_nucleus")) {
            builder.step_nucleus.end_list();
        }
        if (builder.fields.contains("step_position")) {
            builder.step_position.content<0>().end_list();
            builder.step_position.content<1>().end_list();
            builder.step_position.content<2>().end_list();
        }
        if (builder.fields.contains("step_momentum")) {
            builder.step_momentum.content<0>().end_list();
            builder.step_momentum.content<1>().end_list();
            builder.step_momentum.content<2>().end_list();
        }
    }
}


void InsertTrackBegin(const G4Track* track, Builders& builder) {
    if (builder.fields.contains("step_energy")) {
        builder.step_energy.content().begin_list();
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.content().begin_list();
    }
    if (builder.fields.contains("step_track_kinetic_energy")) {
        builder.step_track_kinetic_energy.content().begin_list();
    }
    if (builder.fields.contains("step_process")) {
        builder.step_process.content().begin_list();
    }
    if (builder.fields.contains("step_process_type")) {
        builder.step_process_type.content().begin_list();
    }
    if (builder.fields.contains("step_volume")) {
        builder.step_volume.content().begin_list();
    }
    if (builder.fields.contains("step_volume_post")) {
        builder.step_volume_post.content().begin_list();
    }
    if (builder.fields.contains("step_nucleus")) {
        builder.step_nucleus.content().begin_list();
    }
    if (builder.fields.contains("step_position")) {
        builder.step_position.content<0>().content().begin_list();
        builder.step_position.content<1>().content().begin_list();
        builder.step_position.content<2>().content().begin_list();
    }
    if (builder.fields.contains("step_momentum")) {
        builder.step_momentum.content<0>().content().begin_list();
        builder.step_momentum.content<1>().content().begin_list();
        builder.step_momentum.content<2>().content().begin_list();
    }
}

void InsertTrackEnd(const G4Track* track, Builders& builder) {
    // insert secondary ids
    if (builder.fields.contains("track_children_ids")) {
        builder.track_children_ids.content().begin_list();
        // TODO
        builder.track_children_ids.content().end_list();
    }
    //
    if (builder.fields.contains("step_energy")) {
        builder.step_energy.content().end_list();
    }
    if (builder.fields.contains("step_time")) {
        builder.step_time.content().end_list();
    }
    if (builder.fields.contains("step_track_kinetic_energy")) {
        builder.step_track_kinetic_energy.content().end_list();
    }
    if (builder.fields.contains("step_process")) {
        builder.step_process.content().end_list();
    }
    if (builder.fields.contains("step_process_type")) {
        builder.step_process_type.content().end_list();
    }
    if (builder.fields.contains("step_volume")) {
        builder.step_volume.content().end_list();
    }
    if (builder.fields.contains("step_volume_post")) {
        builder.step_volume_post.content().end_list();
    }
    if (builder.fields.contains("step_nucleus")) {
        builder.step_nucleus.content().end_list();
    }
    if (builder.fields.contains("step_position")) {
        builder.step_position.content<0>().content().end_list();
        builder.step_position.content<1>().content().end_list();
        builder.step_position.content<2>().content().end_list();
    }
    if (builder.fields.contains("step_momentum")) {
        builder.step_momentum.content<0>().content().end_list();
        builder.step_momentum.content<1>().content().end_list();
        builder.step_momentum.content<2>().content().end_list();
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
    if (builder.fields.contains("track_initial_momentum_x")) {
        builder.track_initial_momentum_x.content().append(track->GetVertexMomentumDirection().x());
    }
    if (builder.fields.contains("track_initial_momentum_y")) {
        builder.track_initial_momentum_y.content().append(track->GetVertexMomentumDirection().y());
    }
    if (builder.fields.contains("track_initial_momentum_z")) {
        builder.track_initial_momentum_z.content().append(track->GetVertexMomentumDirection().z());
    }
    if (builder.fields.contains("track_weight")) {
        builder.track_weight.content().append(track->GetWeight());
    }
    if (builder.fields.contains("track_particle")) {
        const auto& particleName = track->GetParticleDefinition()->GetParticleName();
        builder.track_particle.content().append_string(particleName);
    }
    if (builder.fields.contains("track_particle_type")) {
        const auto& particleTypeName = track->GetParticleDefinition()->GetParticleType();
        builder.track_particle_type.content().append_string(particleTypeName);
    }
    if (builder.fields.contains("track_creator_process")) {
        string creatorProcessName = "InitProcess";
        const auto creatorProcess = track->GetCreatorProcess();
        if (creatorProcess != nullptr) {
            creatorProcessName = creatorProcess->GetProcessName();
        }
        builder.track_creator_process.content().append_string(creatorProcessName);
    }
    if (builder.fields.contains("track_creator_process_type")) {
        string creatorProcessTypeName = "InitProcess";
        const auto& creatorProcess = track->GetCreatorProcess();
        if (creatorProcess != nullptr) {
            creatorProcessTypeName = G4VProcess::GetProcessTypeName(creatorProcess->GetProcessType());
        }
        builder.track_creator_process_type.content().append_string(creatorProcessTypeName);
    }
}

void InsertStep(const G4Step* step, Builders& builder) {
    const G4Track* track = step->GetTrack();

    const auto& stepPost = step->GetPostStepPoint();
    const auto& stepPre = step->GetPreStepPoint();

    const auto process = stepPost->GetProcessDefinedStep();
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
    if (builder.fields.contains("step_position")) {
        builder.step_position.content<0>().content().content().append(stepPost->GetPosition().x() / units::length);
        builder.step_position.content<1>().content().content().append(stepPost->GetPosition().y() / units::length);
        builder.step_position.content<2>().content().content().append(stepPost->GetPosition().z() / units::length);
    }
    if (builder.fields.contains("step_momentum")) {
        builder.step_momentum.content<0>().content().content().append(stepPost->GetMomentumDirection().x());
        builder.step_momentum.content<1>().content().content().append(stepPost->GetMomentumDirection().y());
        builder.step_momentum.content<2>().content().content().append(stepPost->GetMomentumDirection().z());
    }
    if (builder.fields.contains("step_track_kinetic_energy")) {
        builder.step_track_kinetic_energy.content().content().append(stepPost->GetKineticEnergy() / units::energy);
    }
    if (builder.fields.contains("step_process")) {
        builder.step_process.content().content().append_string(processName);
    }
    if (builder.fields.contains("step_process_type")) {
        builder.step_process_type.content().content().append_string(processName);
    }
    if (builder.fields.contains("step_volume")) {
        const auto& volumeName = stepPre->GetPhysicalVolume()->GetName();
        builder.step_volume.content().content().append_string(volumeName);
    }
    if (builder.fields.contains("step_volume_post")) {
        string volumeName = "OutOfWorld";
        const auto volume = stepPost->GetPhysicalVolume();
        if (volume != nullptr) {
            volumeName = volume->GetName();
        }
        builder.step_volume_post.content().content().append_string(volumeName);
    }
    if (builder.fields.contains("step_nucleus")) {
        const auto& nucleus = "";
        // TODO
        builder.step_nucleus.content().content().append_string(nucleus);
    }
}

template<typename T>
py::object snapshot_builder(const T& builder) {
    // How much memory to allocate?
    std::map<std::string, size_t> names_nbytes = {};
    builder.buffer_nbytes(names_nbytes);

    // Allocate memory
    std::map<std::string, void*> buffers = {};
    for (const auto& it: names_nbytes) {
        auto* ptr = new uint8_t[it.second];
        buffers[it.first] = (void*) ptr;
    }

    // Write non-contiguous contents to memory
    builder.to_buffers(buffers);
    auto from_buffers = py::module::import("awkward").attr("from_buffers");

    // Build Python dictionary containing arrays
    // dtypes not important here as long as they match the underlying buffer
    // as Awkward Array calls `frombuffer` to convert to the correct type
    py::dict container;
    for (const auto& it: buffers) {

        // Create capsule that frees the allocated data when out of scope
        py::capsule free_when_done(it.second, [](void* data) {
            auto* dataPtr = reinterpret_cast<uint8_t*>(data);
            delete[] dataPtr;
        });

        // Adopt the memory filled by `to_buffers` as a NumPy array
        // We only need to return a "buffer" here, but py::array_t let's
        // us associate a capsule for destruction, which means that
        // Python can own this memory. Therefore, we use py::array_t
        auto* data = reinterpret_cast<uint8_t*>(it.second);
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
    if (builder.fields.contains("run")) {
        snapshot["run"] = snapshot_builder(builder.run);
    }
    if (builder.fields.contains("id")) {
        snapshot["id"] = snapshot_builder(builder.id);
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
    if (builder.fields.contains("track_weight")) {
        snapshot["track_weight"] = snapshot_builder(builder.track_weight);
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
    if (builder.fields.contains("track_initial_momentum_x")) {
        snapshot["track_initial_momentum_x"] = snapshot_builder(builder.track_initial_momentum_x);
    }
    if (builder.fields.contains("track_initial_momentum_y")) {
        snapshot["track_initial_momentum_y"] = snapshot_builder(builder.track_initial_momentum_y);
    }
    if (builder.fields.contains("track_initial_momentum_z")) {
        snapshot["track_initial_momentum_z"] = snapshot_builder(builder.track_initial_momentum_z);
    }
    if (builder.fields.contains("track_particle")) {
        snapshot["track_particle"] = snapshot_builder(builder.track_particle);
    }
    if (builder.fields.contains("track_particle_type")) {
        snapshot["track_particle_type"] = snapshot_builder(builder.track_particle_type);
    }
    if (builder.fields.contains("track_creator_process")) {
        snapshot["track_creator_process"] = snapshot_builder(builder.track_creator_process);
    }
    if (builder.fields.contains("track_creator_process_type")) {
        snapshot["track_creator_process_type"] = snapshot_builder(builder.track_creator_process_type);
    }
    if (builder.fields.contains("track_children_ids")) {
        snapshot["track_children_ids"] = snapshot_builder(builder.track_children_ids);
    }
    if (builder.fields.contains("step_energy")) {
        snapshot["step_energy"] = snapshot_builder(builder.step_energy);
    }
    if (builder.fields.contains("step_time")) {
        snapshot["step_time"] = snapshot_builder(builder.step_time);
    }
    if (builder.fields.contains("step_track_kinetic_energy")) {
        snapshot["step_track_kinetic_energy"] = snapshot_builder(builder.step_track_kinetic_energy);
    }
    if (builder.fields.contains("step_process")) {
        snapshot["step_process"] = snapshot_builder(builder.step_process);
    }
    if (builder.fields.contains("step_process_type")) {
        snapshot["step_process_type"] = snapshot_builder(builder.step_process_type);
    }
    if (builder.fields.contains("step_volume")) {
        snapshot["step_volume"] = snapshot_builder(builder.step_volume);
    }
    if (builder.fields.contains("step_volume_post")) {
        snapshot["step_volume_post"] = snapshot_builder(builder.step_volume_post);
    }
    if (builder.fields.contains("step_nucleus")) {
        snapshot["step_nucleus"] = snapshot_builder(builder.step_nucleus);
    }
    snapshot["step_position"] = snapshot_builder(builder.step_position);
    snapshot["step_momentum"] = snapshot_builder(builder.step_momentum);
    return snapshot;
}

}// namespace geant4_app::data
