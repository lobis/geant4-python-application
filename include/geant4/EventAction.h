
#ifndef GEANT4_APPLICATION_EVENTACTION_H
#define GEANT4_APPLICATION_EVENTACTION_H

#include <G4Event.hh>
#include <G4UserEventAction.hh>

namespace geant4_app {

class EventAction : public G4UserEventAction {
public:
    EventAction();

    void BeginOfEventAction(const G4Event*) override;

    void EndOfEventAction(const G4Event*) override;
};

}// namespace geant4_app
#endif// GEANT4_APPLICATION_EVENTACTION_H
