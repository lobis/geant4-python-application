
#pragma once

#include <G4UserSteppingAction.hh>

namespace geant4_app {

class SteppingAction : public G4UserSteppingAction {
public:
    SteppingAction();

    void UserSteppingAction(const G4Step*) override;
};

}// namespace geant4_app
