
#pragma once

#include <G4Event.hh>
#include <G4UserEventAction.hh>

namespace geant4_app {

class EventAction : public G4UserEventAction {
public:
    EventAction();

    void BeginOfEventAction(const G4Event*) override;

    void EndOfEventAction(const G4Event*) override;

    static double sensitiveEnergy;
};

}// namespace geant4_app
