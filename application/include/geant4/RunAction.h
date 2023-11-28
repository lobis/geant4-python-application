
#ifndef GEANT4_APPLICATION_RUNACTION_H
#define GEANT4_APPLICATION_RUNACTION_H

#include <G4UserRunAction.hh>

#include "awkward/LayoutBuilder.h"

class RunAction : public G4UserRunAction {
public:
    RunAction();

    void BeginOfRunAction(const G4Run*) override;

    void EndOfRunAction(const G4Run*) override;
};

#endif// GEANT4_APPLICATION_RUNACTION_H
