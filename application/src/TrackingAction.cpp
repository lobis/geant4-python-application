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

#include "geant4/RunManager.h"

using namespace std;

TrackingAction::TrackingAction() : G4UserTrackingAction() {}

void TrackingAction::PreUserTrackingAction(const G4Track* track) {
    auto runManager = dynamic_cast<RunManager*>(G4RunManager::GetRunManager());
}

void TrackingAction::PostUserTrackingAction(const G4Track* track) {
    auto runManager = dynamic_cast<RunManager*>(G4RunManager::GetRunManager());
}
