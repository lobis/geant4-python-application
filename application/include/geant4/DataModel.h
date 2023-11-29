#ifndef GEANT4PYTHONICAPPLICATION_DATAMODEL_H
#define GEANT4PYTHONICAPPLICATION_DATAMODEL_H

#include "awkward/LayoutBuilder.h"

class G4Event;
class G4Track;
class G4Step;

namespace geant4::data {

// Enum to represent fields
enum Field : std::size_t { energy,
                           time };

using UserDefinedMap = std::map<std::size_t, std::string>;


template<std::size_t field_name, class BUILDER>
using RecordField = awkward::LayoutBuilder::Field<field_name, BUILDER>;

template<class... BUILDERS>
using RecordBuilder = awkward::LayoutBuilder::Record<UserDefinedMap, BUILDERS...>;

template<class PRIMITIVE>
using NumpyBuilder = awkward::LayoutBuilder::Numpy<PRIMITIVE>;

using Builder = RecordBuilder<RecordField<static_cast<std::size_t>(Field::energy), NumpyBuilder<double>>,
                              RecordField<static_cast<std::size_t>(Field::time), NumpyBuilder<double>>>;


void InsertEvent(const G4Event* track, Builder& builder);
void InsertTrack(const G4Track* track, Builder& builder);
void InsertStep(const G4Event* track, Builder& builder);

}// namespace geant4::data


#endif// GEANT4PYTHONICAPPLICATION_DATAMODEL_H
