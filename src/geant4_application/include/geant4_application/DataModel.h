
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
using TrackFieldBuilder = ListOffsetBuilder<unsigned int, NumpyBuilder<T>>;

template<class PRIMITIVE>
using StringBuilder = awkward::LayoutBuilder::String<PRIMITIVE>;

template<class PRIMITIVE>
class VectorBuilder : public RecordBuilder<
                              RecordField<0, NumpyBuilder<double>>,
                              RecordField<1, NumpyBuilder<double>>,
                              RecordField<2, NumpyBuilder<double>>> {
public:
    VectorBuilder() : RecordBuilder<
                              RecordField<0, NumpyBuilder<double>>,
                              RecordField<1, NumpyBuilder<double>>,
                              RecordField<2, NumpyBuilder<double>>>() {}

    void append(const G4ThreeVector& vector) {
        this->content<0>().append(vector.x());
        this->content<1>().append(vector.y());
        this->content<2>().append(vector.z());
    }
};

template<class T>
class PositionVectorBuilder : public VectorBuilder<T> {
public:
    PositionVectorBuilder() : VectorBuilder<T>() {
        this->set_fields({{0, "x"}, {1, "y"}, {2, "z"}});
        this->set_parameters(R"""("__record__": "Vector3D")""");
    }
};

template<class T>
class MomentumVectorBuilder : public VectorBuilder<T> {
public:
    MomentumVectorBuilder() : VectorBuilder<T>() {
        this->set_fields({{0, "px"}, {1, "py"}, {2, "pz"}});
        this->set_parameters(R"""("__record__": "Momentum3D")""");
    }
};

template<class T>
using StepFieldBuilder = ListOffsetBuilder<unsigned int, ListOffsetBuilder<unsigned int, NumpyBuilder<T>>>;

using TrackStringBuilder = ListOffsetBuilder<unsigned int, StringBuilder<unsigned int>>;
using StepStringBuilder = ListOffsetBuilder<unsigned int, ListOffsetBuilder<unsigned int, StringBuilder<unsigned int>>>;

template<class T>
using TrackPositionBuilder = ListOffsetBuilder<unsigned int,
                                               PositionVectorBuilder<T>>;

template<class T>
using TrackMomentumBuilder = ListOffsetBuilder<unsigned int,
                                               MomentumVectorBuilder<T>>;

template<class T>
using StepPositionBuilder = ListOffsetBuilder<unsigned int,
                                              ListOffsetBuilder<unsigned int,
                                                                PositionVectorBuilder<T>>>;

template<class T>
using StepMomentumBuilder = ListOffsetBuilder<unsigned int,
                                              ListOffsetBuilder<unsigned int,
                                                                MomentumVectorBuilder<T>>>;

template<class PRIMITIVE>
using PrimariesBuilderBase = RecordBuilder<
        RecordField<0, StringBuilder<PRIMITIVE>>,     // particle. TODO: use PDG / particle
        RecordField<1, NumpyBuilder<double>>,         // energy
        RecordField<2, PositionVectorBuilder<double>>,// position
        RecordField<3, MomentumVectorBuilder<double>> // direction
        >;

template<class PRIMITIVE>
class PrimariesBuilder : public PrimariesBuilderBase<PRIMITIVE> {
public:
    PrimariesBuilder() : PrimariesBuilderBase<PRIMITIVE>() {
        this->set_fields({{0, "particle"}, {1, "energy"}, {2, "position"}, {3, "direction"}});
        this->set_parameters(R"""("__record__": "primaries")""");// not used for anything at the moment
    }
};

struct Builders {
    std::unordered_set<std::string> fields;

    // event
    NumpyBuilder<unsigned int> run;
    NumpyBuilder<unsigned int> id;
    // primaries (a single event can have multiple primaries)
    ListOffsetBuilder<unsigned int, PrimariesBuilder<unsigned int>> primaries;
    // tracks
    TrackFieldBuilder<unsigned int> track_id;
    TrackFieldBuilder<unsigned int> track_parent_id;
    TrackFieldBuilder<double> track_initial_energy;
    TrackFieldBuilder<double> track_initial_time;
    TrackPositionBuilder<double> track_initial_position;
    TrackMomentumBuilder<double> track_initial_momentum;
    StepFieldBuilder<unsigned int> track_children_ids;// this is a track field, but it has the same structure of a step field
    TrackStringBuilder track_particle;
    TrackStringBuilder track_particle_type;
    TrackStringBuilder track_creator_process;
    TrackStringBuilder track_creator_process_type;
    TrackFieldBuilder<double> track_weight;

    // steps
    StepFieldBuilder<double> step_energy;
    StepFieldBuilder<double> step_time;
    StepFieldBuilder<double> step_track_kinetic_energy;
    StepStringBuilder step_process;
    StepStringBuilder step_process_type;
    StepStringBuilder step_volume;
    StepStringBuilder step_volume_post;
    StepStringBuilder step_nucleus;
    StepPositionBuilder<double> step_position;
    StepMomentumBuilder<double> step_momentum;

    Builders(const std::unordered_set<std::string>& fields) : fields(fields) {};
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
