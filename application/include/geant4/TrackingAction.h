//
// Created by Luis Antonio Obis Aparicio on 25/11/23.
//

#ifndef GEANT4_APPLICATION_TRACKINGACTION_H
#define GEANT4_APPLICATION_TRACKINGACTION_H

#include <G4UserTrackingAction.hh>

class TrackingAction : public G4UserTrackingAction {
public:
    TrackingAction();

    void PreUserTrackingAction(const G4Track*) override;
    void PostUserTrackingAction(const G4Track*) override;
};

#endif// GEANT4_APPLICATION_TRACKINGACTION_H
