
#pragma once

#include <G4SteppingManager.hh>
#include <G4SteppingVerbose.hh>
#include <G4VSteppingVerbose.hh>

namespace geant4_app {

class SteppingVerbose : public G4SteppingVerbose {
public:
    SteppingVerbose();

    void TrackingStarted() override;
    void StepInfo() override;

    void Initialize();
};

}// namespace geant4_app
