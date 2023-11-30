
#include "geant4/TrackingAction.h"
#include "geant4/RunAction.h"

#include <G4ParticleDefinition.hh>
#include <G4ParticleTypes.hh>
#include <G4SystemOfUnits.hh>
#include <G4Track.hh>
#include <G4UnitsTable.hh>
#include <G4ios.hh>
#include <iostream>

using namespace std;

TrackingAction::TrackingAction() : G4UserTrackingAction() {}

void TrackingAction::PreUserTrackingAction(const G4Track* track) {
    geant4::data::InsertTrackBegin(track, RunAction::GetBuilder());
    geant4::data::InsertTrack(track, RunAction::GetBuilder());
}

void TrackingAction::PostUserTrackingAction(const G4Track* track) {
    geant4::data::InsertTrackEnd(track, RunAction::GetBuilder());
}
