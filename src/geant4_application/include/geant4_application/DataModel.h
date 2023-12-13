
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

typedef unsigned int id;

template<class T>
using TrackFieldBuilder = ListOffsetBuilder<id, NumpyBuilder<T>>;

template<class T>
using StepFieldBuilder = ListOffsetBuilder<id, ListOffsetBuilder<id, NumpyBuilder<T>>>;

struct Builders {
    std::unordered_set<std::string> fields;
    NumpyBuilder<id> run_id;
    NumpyBuilder<id> event_id;
    TrackFieldBuilder<id> track_id;
    TrackFieldBuilder<id> track_parent_id;
    TrackFieldBuilder<float> track_initial_energy;
    TrackFieldBuilder<float> track_initial_time;
    TrackFieldBuilder<float> track_initial_position_x;
    TrackFieldBuilder<float> track_initial_position_y;
    TrackFieldBuilder<float> track_initial_position_z;
    StepFieldBuilder<float> step_energy;
    StepFieldBuilder<float> step_time;
    StepFieldBuilder<float> step_position_x;
    StepFieldBuilder<float> step_position_y;
    StepFieldBuilder<float> step_position_z;

    Builders(const std::unordered_set<std::string>& fields) : fields(fields){};

    void Clear() {
        run_id.clear();
        event_id.clear();
        track_id.clear();
        track_parent_id.clear();
        track_initial_energy.clear();
        track_initial_time.clear();
        track_initial_position_x.clear();
        track_initial_position_y.clear();
        track_initial_position_z.clear();
        step_energy.clear();
        step_time.clear();
        step_position_x.clear();
        step_position_y.clear();
        step_position_z.clear();
    }
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
