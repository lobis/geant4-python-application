#ifndef GEANT4PYTHONICAPPLICATION_DATAMODEL_H
#define GEANT4PYTHONICAPPLICATION_DATAMODEL_H

#include "awkward/LayoutBuilder.h"

class G4Event;
class G4Track;
class G4Step;

namespace geant4::data {

enum Field : std::size_t { eventId,
                           trackId,
                           trackParentId,
                           trackEnergy,
                           trackTime,
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
using Builder = RecordBuilder<RecordField<static_cast<std::size_t>(Field::eventId), NumpyBuilder<id>>,
                              RecordField<static_cast<std::size_t>(Field::trackId), ListOffsetBuilder<id, NumpyBuilder<id>>>,
                              RecordField<static_cast<std::size_t>(Field::trackParentId), ListOffsetBuilder<id, NumpyBuilder<id>>>,
                              RecordField<static_cast<std::size_t>(Field::trackEnergy), ListOffsetBuilder<id, NumpyBuilder<float>>>,
                              RecordField<static_cast<std::size_t>(Field::trackTime), ListOffsetBuilder<id, NumpyBuilder<float>>>>;


void InsertEventBegin(const G4Event* event, Builder& builder);
void InsertEventEnd(const G4Event* event, Builder& builder);
void InsertTrackBegin(const G4Track* track, Builder& builder);
void InsertTrackEnd(const G4Track* track, Builder& builder);
void InsertStep(const G4Step* step, Builder& builder);

}// namespace geant4::data


#endif// GEANT4PYTHONICAPPLICATION_DATAMODEL_H
