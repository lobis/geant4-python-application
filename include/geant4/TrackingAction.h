
#include <G4UserTrackingAction.hh>

namespace geant4_app {

class TrackingAction : public G4UserTrackingAction {
public:
    TrackingAction();

    void PreUserTrackingAction(const G4Track*) override;
    void PostUserTrackingAction(const G4Track*) override;
};

}// namespace geant4_app
