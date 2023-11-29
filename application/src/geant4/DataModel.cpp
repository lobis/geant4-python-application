
#include "geant4/DataModel.h"

#include <G4Event.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTypes.hh>
#include <G4Step.hh>
#include <G4SystemOfUnits.hh>
#include <G4Track.hh>
#include <G4UnitsTable.hh>
#include <iostream>


using namespace geant4::data;

void InsertEvent(const G4Event* event, Builder& builder) {
}

void InsertTrack(const G4Track* track, Builder& builder) {
    auto& energyBuilder = builder.content<Field::energy>();
    auto& timeBuilder = builder.content<Field::time>();

    energyBuilder.append(track->GetKineticEnergy());
    timeBuilder.append(track->GetGlobalTime());
}

void InsertStep(const G4Step* step, Builder& builder) {
}
