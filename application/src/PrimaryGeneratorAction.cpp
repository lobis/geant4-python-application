
#include "geant4/PrimaryGeneratorAction.h"

#include "G4Event.hh"
#include "G4GeneralParticleSource.hh"
#include "G4ParticleDefinition.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"
#include "G4VUserPrimaryGeneratorAction.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction() : G4VUserPrimaryGeneratorAction(), particleGun(1) {
    G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
    G4ParticleDefinition* particle = particleTable->FindParticle("e-");

    particleGun.SetParticleDefinition(particle);
    particleGun.SetParticleEnergy(1.0 * MeV);
    particleGun.SetParticlePosition(G4ThreeVector(0.0, 0.0, -10.0 * cm));
    particleGun.SetParticleMomentumDirection(G4ThreeVector(0.0, 0.0, 1.0));
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) { particleGun.GeneratePrimaryVertex(event); }
