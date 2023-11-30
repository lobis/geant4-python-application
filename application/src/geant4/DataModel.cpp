
#include "geant4/DataModel.h"

#include <G4Event.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTypes.hh>
#include <G4Step.hh>
#include <G4SystemOfUnits.hh>
#include <G4Track.hh>
#include <G4UnitsTable.hh>
#include <iostream>

using namespace std;

namespace geant4::data {

void InsertEventBegin(const G4Event* event, Builder& builder) {
    builder.content<Field::eventId>().append(event->GetEventID());

    auto& trackId = builder.content<Field::trackId>();
    auto& trackParentId = builder.content<Field::trackParentId>();
    auto& trackEnergy = builder.content<Field::trackEnergy>();
    auto& trackTime = builder.content<Field::trackTime>();

    trackId.begin_list();
    trackParentId.begin_list();
    trackEnergy.begin_list();
    trackTime.begin_list();
}

void InsertEventEnd(const G4Event*, Builder& builder) {

    auto& trackId = builder.content<Field::trackId>();
    auto& trackParentId = builder.content<Field::trackParentId>();
    auto& trackEnergy = builder.content<Field::trackEnergy>();
    auto& trackTime = builder.content<Field::trackTime>();

    trackId.end_list();
    trackParentId.end_list();
    trackEnergy.end_list();
    trackTime.end_list();
}

void InsertTrackBegin(const G4Track* track, Builder& builder) {
    auto& trackId = builder.content<Field::trackId>();
    auto& trackParentId = builder.content<Field::trackParentId>();
    auto& trackEnergy = builder.content<Field::trackEnergy>();
    auto& trackTime = builder.content<Field::trackTime>();

    trackId.content().append(track->GetTrackID());
    trackParentId.content().append(track->GetParentID());
    trackEnergy.content().append(track->GetKineticEnergy() / units::energy);
    trackTime.content().append(track->GetGlobalTime() / units::time);
    // is there a way to get the ref to the output of begin_list without having to pass it around?
}

void InsertTrackEnd(const G4Track* track, Builder& builder) {
}

void InsertStep(const G4Step* step, Builder& builder) {
}

}// namespace geant4::data
