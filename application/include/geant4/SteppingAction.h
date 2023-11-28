
#ifndef GEANT4_APPLICATION_STEPPINGACTION_H
#define GEANT4_APPLICATION_STEPPINGACTION_H

#include <G4UserSteppingAction.hh>

class SteppingAction : public G4UserSteppingAction {
public:
    SteppingAction();

    void UserSteppingAction(const G4Step*) override;
};

#endif// GEANT4_APPLICATION_STEPPINGACTION_H
