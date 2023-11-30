
#include "geant4/DataModel.h"

#include <G4Event.hh>
#include <G4HadronicProcess.hh>
#include <G4Nucleus.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTypes.hh>
#include <G4Run.hh>
#include <G4RunManager.hh>
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
    builder.content<Field::runId>().append(G4RunManager::GetRunManager()->GetCurrentRun()->GetRunID());
    builder.content<Field::eventId>().append(event->GetEventID());
    //
    builder.content<Field::trackId>().begin_list();
    builder.content<Field::trackParentId>().begin_list();
    builder.content<Field::trackInitialEnergy>().begin_list();
    builder.content<Field::trackInitialTime>().begin_list();
    builder.content<Field::trackInitialPositionX>().begin_list();
    builder.content<Field::trackInitialPositionY>().begin_list();
    builder.content<Field::trackInitialPositionZ>().begin_list();
    builder.content<Field::trackInitialMomentumX>().begin_list();
    builder.content<Field::trackInitialMomentumY>().begin_list();
    builder.content<Field::trackInitialMomentumZ>().begin_list();
    builder.content<Field::trackWeight>().begin_list();
    //
    builder.content<Field::hitsEnergy>().begin_list();
    builder.content<Field::hitsTime>().begin_list();
    builder.content<Field::hitsPositionX>().begin_list();
    builder.content<Field::hitsPositionY>().begin_list();
    builder.content<Field::hitsPositionZ>().begin_list();
    builder.content<Field::hitsTrackKineticEnergy>().begin_list();

    // builder.content<Field::hitsProcess>().begin_list();
}

void InsertEventEnd(const G4Event*, Builder& builder) {
    builder.content<Field::trackId>().end_list();
    builder.content<Field::trackParentId>().end_list();
    builder.content<Field::trackInitialEnergy>().end_list();
    builder.content<Field::trackInitialTime>().end_list();
    // builder.content<Field::trackCreatorProcess>().end_list();
    // builder.content<Field::trackCreatorProcessType>().end_list();
    builder.content<Field::trackInitialPositionX>().end_list();
    builder.content<Field::trackInitialPositionY>().end_list();
    builder.content<Field::trackInitialPositionZ>().end_list();
    builder.content<Field::trackInitialMomentumX>().end_list();
    builder.content<Field::trackInitialMomentumY>().end_list();
    builder.content<Field::trackInitialMomentumZ>().end_list();
    builder.content<Field::trackWeight>().end_list();
    //
    builder.content<Field::hitsEnergy>().end_list();
    builder.content<Field::hitsTime>().end_list();
    // builder.content<Field::hitsProcess>().end_list();
    // builder.content<Field::hitsProcessType>().end_list();
    // builder.content<Field::hitsVolume>().end_list();
    builder.content<Field::hitsPositionX>().end_list();
    builder.content<Field::hitsPositionY>().end_list();
    builder.content<Field::hitsPositionZ>().end_list();
    builder.content<Field::hitsTrackKineticEnergy>().end_list();
}

void InsertTrackBegin(const G4Track* track, Builder& builder) {
    builder.content<Field::trackId>().content().append(track->GetTrackID());
    builder.content<Field::trackParentId>().content().append(track->GetParentID());
    builder.content<Field::trackInitialEnergy>().content().append(track->GetKineticEnergy() / units::energy);
    builder.content<Field::trackInitialTime>().content().append(track->GetGlobalTime() / units::time);
    // builder.content<Field::trackCreatorProcess>().content().append(track->GetCreatorProcess()->GetProcessName());
    // builder.content<Field::trackCreatorProcessType>().content().append(G4VProcess::GetProcessTypeName(track->GetCreatorProcess()->GetProcessType()));
    builder.content<Field::trackInitialPositionX>().content().append(track->GetPosition().x() / units::length);
    builder.content<Field::trackInitialPositionY>().content().append(track->GetPosition().y() / units::length);
    builder.content<Field::trackInitialPositionZ>().content().append(track->GetPosition().z() / units::length);
    builder.content<Field::trackInitialMomentumX>().content().append(track->GetMomentum().x() / units::momentum);
    builder.content<Field::trackInitialMomentumY>().content().append(track->GetMomentum().y() / units::momentum);
    builder.content<Field::trackInitialMomentumZ>().content().append(track->GetMomentum().z() / units::momentum);
    builder.content<Field::trackWeight>().content().append(track->GetWeight());
    //
    builder.content<Field::hitsEnergy>().content().begin_list();
    builder.content<Field::hitsTime>().content().begin_list();
    // builder.content<Field::hitsProcess>().content().begin_list();
    // builder.content<Field::hitsProcessType>().content().begin_list();
    // builder.content<Field::hitsVolume>().content().begin_list();
    builder.content<Field::hitsPositionX>().content().begin_list();
    builder.content<Field::hitsPositionY>().content().begin_list();
    builder.content<Field::hitsPositionZ>().content().begin_list();
    builder.content<Field::hitsTrackKineticEnergy>().content().begin_list();

    // we should probably insert a step here to mark the beginning of the track / use stepping verbose
}

void InsertTrackEnd(const G4Track*, Builder& builder) {
    builder.content<Field::hitsEnergy>().content().end_list();
    builder.content<Field::hitsTime>().content().end_list();
    // builder.content<Field::hitsProcess>().content().end_list();
    // builder.content<Field::hitsProcessType>().content().end_list();
    // builder.content<Field::hitsVolume>().content().end_list();
    builder.content<Field::hitsPositionX>().content().end_list();
    builder.content<Field::hitsPositionY>().content().end_list();
    builder.content<Field::hitsPositionZ>().content().end_list();
    builder.content<Field::hitsTrackKineticEnergy>().content().end_list();
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
    // builder.content<Field::hitsProcessType>().content().content().append(processTypeName);
    // builder.content<Field::hitsVolume>().content().content().append(stepPost->GetPhysicalVolume()->GetName());
    builder.content<Field::hitsPositionX>().content().content().append(stepPost->GetPosition().x() / units::length);
    builder.content<Field::hitsPositionY>().content().content().append(stepPost->GetPosition().y() / units::length);
    builder.content<Field::hitsPositionZ>().content().content().append(stepPost->GetPosition().z() / units::length);
    builder.content<Field::hitsTrackKineticEnergy>().content().content().append(stepPost->GetKineticEnergy() / units::energy);
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
