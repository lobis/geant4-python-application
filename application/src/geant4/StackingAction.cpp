
#include "geant4/StackingAction.h"


StackingAction::StackingAction() : G4UserStackingAction() {}

G4ClassificationOfNewTrack StackingAction::ClassifyNewTrack(const G4Track*) { return fUrgent; }

void StackingAction::NewStage() {}
