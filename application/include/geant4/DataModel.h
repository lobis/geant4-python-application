#ifndef GEANT4PYTHONICAPPLICATION_DATAMODEL_H
#define GEANT4PYTHONICAPPLICATION_DATAMODEL_H

#include "awkward/LayoutBuilder.h"

#include <G4SystemOfUnits.hh>
#include <G4UnitsTable.hh>

#include <CLHEP/Units/PhysicalConstants.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

class G4Event;
class G4Track;
class G4Step;

namespace geant4::data {

enum Field : std::size_t {
    runId,
    eventId,
    //
    trackId,
    trackParentId,
    // trackParticle,
    // trackParticleType,
    trackInitialEnergy,
    trackInitialTime,
    // trackCreatorProcess,
    // trackCreatorProcessType,
    trackInitialPositionX,
    trackInitialPositionY,
    trackInitialPositionZ,
    trackInitialMomentumX,
    trackInitialMomentumY,
    trackInitialMomentumZ,
    trackWeight,
    //
    stepEnergy,
    stepTime,
    // stepProcess,
    // stepProcessType,
    // stepVolume,
    stepPositionX,
    stepPositionY,
    stepPositionZ,
    stepTrackKineticEnergy,
};

using UserDefinedMap = std::map<std::size_t, std::string>;

template<std::size_t field_name, class BUILDER>
using RecordField = awkward::LayoutBuilder::Field<field_name, BUILDER>;

template<class... BUILDERS>
using RecordBuilder = awkward::LayoutBuilder::Record<UserDefinedMap, BUILDERS...>;

template<class PRIMITIVE, class BUILDER>
using ListOffsetBuilder = awkward::LayoutBuilder::ListOffset<PRIMITIVE, BUILDER>;

template<class PRIMITIVE>
using NumpyBuilder = awkward::LayoutBuilder::Numpy<PRIMITIVE>;

typedef unsigned int id;
using Builder = RecordBuilder<
        RecordField<static_cast<std::size_t>(Field::runId), NumpyBuilder<id>>,
        RecordField<static_cast<std::size_t>(Field::eventId), NumpyBuilder<id>>,
        //
        RecordField<static_cast<std::size_t>(Field::trackId), ListOffsetBuilder<id, NumpyBuilder<id>>>,
        RecordField<static_cast<std::size_t>(Field::trackParentId), ListOffsetBuilder<id, NumpyBuilder<id>>>,
        // RecordField<static_cast<std::size_t>(Field::trackParticle), ListOffsetBuilder<id, NumpyBuilder<std::string>>>,
        // RecordField<static_cast<std::size_t>(Field::trackParticleType), ListOffsetBuilder<id, NumpyBuilder<std::string>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialEnergy), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialTime), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        // RecordField<static_cast<std::size_t>(Field::trackCreatorProcess), ListOffsetBuilder<id, NumpyBuilder<std::string>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialPositionX), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialPositionY), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialPositionZ), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialMomentumX), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialMomentumY), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackInitialMomentumZ), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        RecordField<static_cast<std::size_t>(Field::trackWeight), ListOffsetBuilder<id, NumpyBuilder<float>>>,
        //
        RecordField<static_cast<std::size_t>(Field::stepEnergy), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<float>>>>,
        RecordField<static_cast<std::size_t>(Field::stepTime), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<float>>>>,
        // RecordField<static_cast<std::size_t>(Field::stepVolume), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<std::string>>>>
        // RecordField<static_cast<std::size_t>(Field::stepProcess), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<std::string>>>>
        // RecordField<static_cast<std::size_t>(Field::stepProcessType), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<std::string>>>>
        RecordField<static_cast<std::size_t>(Field::stepPositionX), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<float>>>>,
        RecordField<static_cast<std::size_t>(Field::stepPositionY), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<float>>>>,
        RecordField<static_cast<std::size_t>(Field::stepPositionZ), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<float>>>>,
        RecordField<static_cast<std::size_t>(Field::stepTrackKineticEnergy), ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<float>>>>
        //
        >;

inline Builder MakeBuilder() {
    return {
            {
                    {Field::runId, "run_id"},
                    {Field::eventId, "event_id"},
                    //
                    {Field::trackId, "track.id"},
                    {Field::trackParentId, "track.parent_id"},
                    {Field::trackInitialEnergy, "track.energy"},
                    {Field::trackInitialTime, "track.time"},
                    {Field::trackInitialPositionX, "track.position.x"},
                    {Field::trackInitialPositionY, "track.position.y"},
                    {Field::trackInitialPositionZ, "track.position.z"},
                    {Field::trackInitialMomentumX, "track.momentum.x"},
                    {Field::trackInitialMomentumY, "track.momentum.y"},
                    {Field::trackInitialMomentumZ, "track.momentum.z"},
                    {Field::trackWeight, "track.weight"},
                    //
                    {Field::stepEnergy, "track.step.energy"},
                    {Field::stepTime, "track.step.time"},
                    {Field::stepPositionX, "track.step.position.x"},
                    {Field::stepPositionY, "track.step.position.y"},
                    {Field::stepPositionZ, "track.step.position.z"},
                    {Field::stepTrackKineticEnergy, "track.step.track_kinetic_energy"},

                    // {Field::stepProcess, "track.step.process"}},
                    // {Field::stepProcessType, "track.step.process_type"}},
                    // {Field::stepVolume, "track.step.volume"}},
            }};
}

void InsertEventBegin(const G4Event* event, Builder& builder);
void InsertEventEnd(const G4Event* event, Builder& builder);
void InsertTrackBegin(const G4Track* track, Builder& builder);
void InsertTrackEnd(const G4Track* track, Builder& builder);
void InsertStep(const G4Step* step, Builder& builder);

py::object SnapshotBuilder(Builder& builder);

namespace units {
static constexpr auto energy = CLHEP::keV;
static constexpr auto time = CLHEP::us;
static constexpr auto length = CLHEP::mm;
static constexpr auto momentum = CLHEP::GeV / CLHEP::c_light;
}// namespace units

}// namespace geant4::data


#endif// GEANT4PYTHONICAPPLICATION_DATAMODEL_H
