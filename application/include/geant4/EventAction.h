
#ifndef GEANT4_APPLICATION_EVENTACTION_H
#define GEANT4_APPLICATION_EVENTACTION_H

#include <G4Event.hh>
#include <G4UserEventAction.hh>

class EventAction : public G4UserEventAction {
public:
    EventAction();

    void BeginOfEventAction(const G4Event*) override;

    void EndOfEventAction(const G4Event*) override;
};

#endif// GEANT4_APPLICATION_EVENTACTION_H
