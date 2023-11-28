//
// Created by Luis Antonio Obis Aparicio on 25/11/23.
//

#include "geant4/TrackingAction.h"

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
}

void TrackingAction::PostUserTrackingAction(const G4Track* track) {
}
