
#include "geant4_application/StackingAction.h"

#include <G4ParticlePropertyTable.hh>
#include <G4Track.hh>

using namespace std;
using namespace geant4_app;

StackingAction::StackingAction() : G4UserStackingAction() {}

G4ClassificationOfNewTrack StackingAction::ClassifyNewTrack(const G4Track* track) {
    const auto particle = track->GetParticleDefinition();
    if (particlesToIgnore.contains(particle->GetParticleName())) {
        return fKill;
    }

    return fUrgent;
}

void StackingAction::NewStage() {}

void StackingAction::SetParticlesToIgnore(const std::set<string>& particles) {
    const auto table = G4ParticleTable::GetParticleTable();
    for (const auto& particle: particles) {
        if (table->FindParticle(particle) == nullptr) {
            throw invalid_argument("Particle '" + particle + "' not found in particle table.");
        }
    }
    particlesToIgnore = particles;
}

std::set<string> StackingAction::particlesToIgnore = {};
