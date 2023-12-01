
#pragma once

#include <G4ParticleDefinition.hh>
#include <G4UserStackingAction.hh>

#include <set>
#include <string>

namespace geant4_app {

class StackingAction : public G4UserStackingAction {
public:
    StackingAction();

    G4ClassificationOfNewTrack ClassifyNewTrack(const G4Track*) override;
    void NewStage() override;

    static std::set<std::string> GetIgnoredParticles();
    static void SetIgnoredParticles(const std::set<std::string>& particles);
    static void IgnoreParticle(const std::string&);
    static void IgnoreParticleUndo(const std::string&);

private:
    static std::set<std::string> particlesToIgnore;
};

}// namespace geant4_app
