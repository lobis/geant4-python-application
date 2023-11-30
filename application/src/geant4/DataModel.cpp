
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
    auto& trackHitsEnergy = builder.content<Field::trackHitsEnergy>();
    auto& trackHitsTime = builder.content<Field::trackHitsTime>();

    trackId.begin_list();
    trackParentId.begin_list();
    trackEnergy.begin_list();
    trackTime.begin_list();
    trackHitsEnergy.begin_list();
    trackHitsTime.begin_list();
}

void InsertEventEnd(const G4Event*, Builder& builder) {

    auto& trackId = builder.content<Field::trackId>();
    auto& trackParentId = builder.content<Field::trackParentId>();
    auto& trackEnergy = builder.content<Field::trackEnergy>();
    auto& trackTime = builder.content<Field::trackTime>();
    auto& trackHitsEnergy = builder.content<Field::trackHitsEnergy>();
    auto& trackHitsTime = builder.content<Field::trackHitsTime>();

    trackId.end_list();
    trackParentId.end_list();
    trackEnergy.end_list();
    trackTime.end_list();
    trackHitsEnergy.end_list();
    trackHitsTime.end_list();
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

    builder.content<Field::trackHitsEnergy>().content().begin_list();
    builder.content<Field::trackHitsTime>().content().begin_list();

    // we should probably insert a step here to mark the beginning of the track
}

void InsertTrackEnd(const G4Track*, Builder& builder) {
    auto& trackHitsEnergy = builder.content<Field::trackHitsEnergy>();
    auto& trackHitsTime = builder.content<Field::trackHitsTime>();

    trackHitsEnergy.content().end_list();
    trackHitsTime.content().end_list();
}

void InsertStep(const G4Step* step, Builder& builder) {
    auto& trackHitsEnergy = builder.content<Field::trackHitsEnergy>();
    auto& trackHitsTime = builder.content<Field::trackHitsTime>();

    const auto& stepPost = step->GetPostStepPoint();
    const auto& stepPre = step->GetPreStepPoint();

    trackHitsEnergy.content().content().append(step->GetTotalEnergyDeposit() / units::energy);
    trackHitsTime.content().content().append(stepPost->GetGlobalTime() / units::time);
}

}// namespace geant4::data
