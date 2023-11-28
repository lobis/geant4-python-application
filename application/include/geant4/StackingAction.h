
#ifndef LIBGEANT4PYTHONICAPPLICATION_STACKINGACTION_H
#define LIBGEANT4PYTHONICAPPLICATION_STACKINGACTION_H

#include <G4UserStackingAction.hh>

class StackingAction : public G4UserStackingAction {
public:
    StackingAction();

    G4ClassificationOfNewTrack ClassifyNewTrack(const G4Track*) override;
    void NewStage() override;
};


#endif//LIBGEANT4PYTHONICAPPLICATION_STACKINGACTION_H
