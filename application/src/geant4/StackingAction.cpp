
#include "geant4/StackingAction.h"

#include <G4ParticlePropertyTable.hh>
#include <G4Track.hh>

using namespace std;

StackingAction::StackingAction() : G4UserStackingAction() {}

G4ClassificationOfNewTrack StackingAction::ClassifyNewTrack(const G4Track* track) {
    const auto particle = track->GetParticleDefinition();
    if (particlesToIgnore.contains(particle->GetParticleName())) {
        return fKill;
    }

    return fUrgent;
}

void StackingAction::NewStage() {}

std::set<string> StackingAction::GetIgnoredParticles() {
    return particlesToIgnore;
}

void StackingAction::SetIgnoredParticles(const std::set<string>& particles) {
    particlesToIgnore = particles;
}

void StackingAction::IgnoreParticle(const string& name) {
    const auto particle = G4ParticleTable::GetParticleTable()->FindParticle(name);
    if (particle == nullptr) {
        throw std::runtime_error("Particle '" + name + "' not found");
    }
    particlesToIgnore.insert(name);
}

void StackingAction::IgnoreParticleUndo(const string& name) {
    const auto particle = G4ParticleTable::GetParticleTable()->FindParticle(name);
    if (particle == nullptr) {
        throw std::runtime_error("Particle '" + name + "' not found");
    }
    particlesToIgnore.erase(name);
}

std::set<string> StackingAction::particlesToIgnore = {};
