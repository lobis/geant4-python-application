
#include "geant4/DataModel.h"

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

namespace geant4_app::data {

void InsertEvent(const G4Event* event, Builder& builder) {
    builder.content<Field::runId>().append(G4RunManager::GetRunManager()->GetCurrentRun()->GetRunID());
    builder.content<Field::eventId>().append(event->GetEventID());
}

template<std::size_t... I>
void InsertEventBeginHelper(Builder& builder) {
    (builder.content<I>().begin_list(), ...);
}

void InsertEventBegin(const G4Event* event, Builder& builder) {
    InsertEventBeginHelper<Field::trackId, Field::trackParentId, Field::trackInitialEnergy, Field::trackInitialTime,
                           Field::trackParticle, Field::trackInitialPositionX, Field::trackInitialPositionY, Field::trackInitialPositionZ,
                           Field::trackInitialMomentumX, Field::trackInitialMomentumY, Field::trackInitialMomentumZ, Field::trackWeight,
                           Field::stepEnergy, Field::stepTime, Field::stepPositionX, Field::stepPositionY, Field::stepPositionZ,
                           Field::stepTrackKineticEnergy>(builder);
}

template<std::size_t... I>
void InsertEventEndHelper(Builder& builder) {
    (builder.content<I>().end_list(), ...);
}

void InsertEventEnd(const G4Event*, Builder& builder) {
    InsertEventEndHelper<Field::trackId, Field::trackParentId, Field::trackInitialEnergy, Field::trackInitialTime,
                         Field::trackParticle, Field::trackInitialPositionX, Field::trackInitialPositionY, Field::trackInitialPositionZ,
                         Field::trackInitialMomentumX, Field::trackInitialMomentumY, Field::trackInitialMomentumZ, Field::trackWeight,
                         Field::stepEnergy, Field::stepTime, Field::stepPositionX, Field::stepPositionY, Field::stepPositionZ,
                         Field::stepTrackKineticEnergy>(builder);
}

void InsertTrack(const G4Track* track, Builder& builder) {
    builder.content<Field::trackId>().content().append(track->GetTrackID());
    builder.content<Field::trackParentId>().content().append(track->GetParentID());
    builder.content<Field::trackParticle>().content().append({});
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
}

template<std::size_t... I>
void InsertTrackBeginHelper(Builder& builder) {
    (builder.content<I>().content().begin_list(), ...);
}

void InsertTrackBegin(const G4Track* track, Builder& builder) {
    InsertTrackBeginHelper<Field::stepEnergy, Field::stepTime, Field::stepPositionX, Field::stepPositionY, Field::stepPositionZ,
                           Field::stepTrackKineticEnergy>(builder);
}

template<std::size_t... I>
void InsertTrackEndHelper(Builder& builder) {
    (builder.content<I>().content().end_list(), ...);
}

void InsertTrackEnd(const G4Track*, Builder& builder) {
    InsertTrackEndHelper<Field::stepEnergy, Field::stepTime, Field::stepPositionX, Field::stepPositionY, Field::stepPositionZ,
                         Field::stepTrackKineticEnergy>(builder);
}

void InsertStep(const G4Step* step, Builder& builder) {
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

    cout << "STEP NUMBER: " << track->GetCurrentStepNumber() << " PROCESS: " << processName << endl;

    builder.content<Field::stepEnergy>().content().content().append(step->GetTotalEnergyDeposit() / units::energy);
    builder.content<Field::stepTime>().content().content().append(stepPost->GetGlobalTime() / units::time);
    // builder.content<Field::stepProcess>().content().content().append(processName);
    // builder.content<Field::stepProcessType>().content().content().append(processTypeName);
    // builder.content<Field::stepVolume>().content().content().append(stepPost->GetPhysicalVolume()->GetName());
    builder.content<Field::stepPositionX>().content().content().append(stepPost->GetPosition().x() / units::length);
    builder.content<Field::stepPositionY>().content().content().append(stepPost->GetPosition().y() / units::length);
    builder.content<Field::stepPositionZ>().content().content().append(stepPost->GetPosition().z() / units::length);
    builder.content<Field::stepTrackKineticEnergy>().content().content().append(stepPost->GetKineticEnergy() / units::energy);
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

Builder MakeBuilder() {
    UserDefinedMap fieldToName;
    for (const auto& m: {fieldToNameEvent, fieldToNameTrack, fieldToNameStep}) {
        fieldToName.insert(m.begin(), m.end());
    }
    return {fieldToName};
}
}// namespace geant4_app::data
