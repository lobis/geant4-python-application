
#ifndef GEANT4PYTHONICAPPLICATION_STEPPINGVERBOSE_H
#define GEANT4PYTHONICAPPLICATION_STEPPINGVERBOSE_H

#include <G4SteppingManager.hh>
#include <G4SteppingVerbose.hh>
#include <G4VSteppingVerbose.hh>

class SteppingVerbose : public G4SteppingVerbose {
public:
    SteppingVerbose();

    void TrackingStarted() override;
    void StepInfo() override;
};

#endif//GEANT4PYTHONICAPPLICATION_STEPPINGVERBOSE_H
