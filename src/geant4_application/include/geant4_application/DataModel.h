
#pragma once

#include "awkward/LayoutBuilder.h"

#include <CLHEP/Units/PhysicalConstants.h>
#include <G4Event.hh>
#include <G4Step.hh>
#include <G4SystemOfUnits.hh>
#include <G4Track.hh>
#include <G4UnitsTable.hh>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace geant4_app::data {

using UserDefinedMap = std::map<std::size_t, std::string>;

template<std::size_t field_name, class BUILDER>
using RecordField = awkward::LayoutBuilder::Field<field_name, BUILDER>;

template<class... BUILDERS>
using RecordBuilder = awkward::LayoutBuilder::Record<UserDefinedMap, BUILDERS...>;

template<class PRIMITIVE, class BUILDER>
using ListOffsetBuilder = awkward::LayoutBuilder::ListOffset<PRIMITIVE, BUILDER>;

template<class PRIMITIVE, class BUILDER>
using IndexedBuilder = awkward::LayoutBuilder::IndexedOption<PRIMITIVE, BUILDER>;

template<class PRIMITIVE>
using NumpyBuilder = awkward::LayoutBuilder::Numpy<PRIMITIVE>;

template<class T>
using TrackFieldBuilder = ListOffsetBuilder<uint, NumpyBuilder<T>>;

template<class T>
using StepFieldBuilder = ListOffsetBuilder<uint, ListOffsetBuilder<uint, NumpyBuilder<T>>>;

using TrackStringBuilder = ListOffsetBuilder<uint, ListOffsetBuilder<uint, NumpyBuilder<uint8_t>>>;
using StepStringBuilder = ListOffsetBuilder<uint, ListOffsetBuilder<uint, ListOffsetBuilder<uint, NumpyBuilder<uint8_t>>>>;

struct Builders {
    std::unordered_set<std::string> fields;
    NumpyBuilder<uint> run;
    NumpyBuilder<uint> id;
    //
    TrackFieldBuilder<uint> track_id;
    TrackFieldBuilder<uint> track_parent_id;
    TrackFieldBuilder<double> track_initial_energy;
    TrackFieldBuilder<double> track_initial_time;
    TrackFieldBuilder<double> track_initial_position_x;
    TrackFieldBuilder<double> track_initial_position_y;
    TrackFieldBuilder<double> track_initial_position_z;
    TrackStringBuilder track_particle;
    StepFieldBuilder<double> step_energy;
    StepFieldBuilder<double> step_time;
    StepFieldBuilder<double> step_position_x;
    StepFieldBuilder<double> step_position_y;
    StepFieldBuilder<double> step_position_z;

    Builders(const std::unordered_set<std::string>& fields) : fields(fields) {
        track_particle.content().set_parameters(R"""("__array__": "string")""");
        track_particle.content().content().set_parameters(R"""("__array__": "char")""");
    };
};


void InsertEventBegin(const G4Event* event, Builders& builder);
void InsertEventEnd(const G4Event* event, Builders& builder);

void InsertTrackBegin(const G4Track* track, Builders& builder);
void InsertTrackEnd(const G4Track* track, Builders& builder);

void InsertEvent(const G4Event* event, Builders& builder);
void InsertTrack(const G4Track* track, Builders& builder);
void InsertStep(const G4Step* step, Builders& builder);

py::object SnapshotBuilder(Builders& builder);

namespace units {
static constexpr auto energy = CLHEP::keV;
static constexpr auto time = CLHEP::us;
static constexpr auto length = CLHEP::mm;
static constexpr auto momentum = CLHEP::GeV / CLHEP::c_light;
}// namespace units

}// namespace geant4_app::data
