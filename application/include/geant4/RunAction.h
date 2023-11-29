
#ifndef GEANT4_APPLICATION_RUNACTION_H
#define GEANT4_APPLICATION_RUNACTION_H

#include <G4RunManager.hh>
#include <G4UserRunAction.hh>

#include "geant4/DataModel.h"

class RunAction : public G4UserRunAction {
public:
    RunAction();

    void BeginOfRunAction(const G4Run*) override;

    void EndOfRunAction(const G4Run*) override;

    geant4::data::Builder& GetBuilder() { return builder; }

private:
    geant4::data::Builder builder;
};

#endif// GEANT4_APPLICATION_RUNACTION_H
