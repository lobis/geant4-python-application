
#include "geant4/DataModel.h"

#include <G4Event.hh>
#include <G4HadronicProcess.hh>
#include <G4Nucleus.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTypes.hh>
#include <G4Step.hh>
#include <G4Track.hh>
#include <G4UnitsTable.hh>
#include <G4VProcess.hh>
#include <iostream>

#include <pybind11/numpy.h>
#include <pybind11/stl.h>

using namespace std;

namespace geant4::data {

void InsertEventBegin(const G4Event* event, Builder& builder) {
    builder.content<Field::eventId>().append(event->GetEventID());

    builder.content<Field::trackId>().begin_list();
    builder.content<Field::trackParentId>().begin_list();
    builder.content<Field::trackInitialEnergy>().begin_list();
    builder.content<Field::trackTime>().begin_list();
    builder.content<Field::hitsEnergy>().begin_list();
    builder.content<Field::hitsTime>().begin_list();
    // builder.content<Field::hitsProcess>().begin_list();
}

void InsertEventEnd(const G4Event*, Builder& builder) {
    builder.content<Field::trackId>().end_list();
    builder.content<Field::trackParentId>().end_list();
    builder.content<Field::trackInitialEnergy>().end_list();
    builder.content<Field::trackTime>().end_list();
    builder.content<Field::hitsEnergy>().end_list();
    builder.content<Field::hitsTime>().end_list();
    // builder.content<Field::hitsProcess>().end_list();
}

void InsertTrackBegin(const G4Track* track, Builder& builder) {
    auto& trackId = builder.content<Field::trackId>();
    auto& trackParentId = builder.content<Field::trackParentId>();
    auto& trackEnergy = builder.content<Field::trackInitialEnergy>();
    auto& trackTime = builder.content<Field::trackTime>();

    trackId.content().append(track->GetTrackID());
    trackParentId.content().append(track->GetParentID());
    trackEnergy.content().append(track->GetKineticEnergy() / units::energy);
    trackTime.content().append(track->GetGlobalTime() / units::time);

    builder.content<Field::hitsEnergy>().content().begin_list();
    builder.content<Field::hitsTime>().content().begin_list();
    // builder.content<Field::hitsProcess>().content().begin_list();

    // we should probably insert a step here to mark the beginning of the track / use stepping verbose
}

void InsertTrackEnd(const G4Track*, Builder& builder) {
    builder.content<Field::hitsEnergy>().content().end_list();
    builder.content<Field::hitsTime>().content().end_list();
    // builder.content<Field::hitsProcess>().content().end_list();
}

void InsertStep(const G4Step* step, Builder& builder) {
    auto& hitsEnergy = builder.content<Field::hitsEnergy>();
    auto& hitsTime = builder.content<Field::hitsTime>();

    const G4Track* track = step->GetTrack();

    const auto& stepPost = step->GetPostStepPoint();
    const auto& stepPre = step->GetPreStepPoint();

    const auto process = step->GetPostStepPoint()->GetProcessDefinedStep();
    G4String processName = "Init";
    G4String processTypeName = "Init";
    if (track->GetCurrentStepNumber() != 0) {
        // 0 = Init step (G4SteppingVerbose) process is not defined for this step
        processName = process->GetProcessName();
        processTypeName = G4VProcess::GetProcessTypeName(process->GetProcessType());
    }

    builder.content<Field::hitsEnergy>().content().content().append(step->GetTotalEnergyDeposit() / units::energy);
    builder.content<Field::hitsTime>().content().content().append(stepPost->GetGlobalTime() / units::time);
    // builder.content<Field::hitsProcess>().content().content().append(processName);
}

py::object SnapshotBuilder(Builder& builder) {
    // How much memory to allocate?
    std::map<std::string, size_t> names_nbytes = {};
    builder.buffer_nbytes(names_nbytes);

    // Allocate memory
    std::map<std::string, void*> buffers = {};
    for (const auto& it: names_nbytes) {
        uint8_t* ptr = new uint8_t[it.second];
        buffers[it.first] = static_cast<void*>(ptr);
    }

    // Write non-contiguous contents to memory
    builder.to_buffers(buffers);
    auto from_buffers = py::module::import("awkward").attr("from_buffers");

    // Build Python dictionary containing arrays
    py::dict container;
    for (const auto& it: buffers) {

        // Create capsule that frees the allocated data when out of scope
        py::capsule free_when_done(it.second, [](void* data) {
            uint8_t* dataPtr = reinterpret_cast<uint8_t*>(data);
            delete[] dataPtr;
        });

        // Adopt the memory filled by `to_buffers` as a NumPy array
        container[py::str(it.first)] = py::array_t<uint8_t>(
                {names_nbytes[it.first]},
                {sizeof(uint8_t)},
                reinterpret_cast<uint8_t*>(it.second),
                free_when_done);
    }

    return from_buffers(builder.form(), builder.length(), container);
}

}// namespace geant4::data
