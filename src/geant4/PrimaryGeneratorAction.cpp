
#include "geant4/PrimaryGeneratorAction.h"
#include "geant4/Application.h"

#include <G4Event.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTable.hh>
#include <G4SystemOfUnits.hh>
#include <G4VUserPrimaryGeneratorAction.hh>

using namespace std;
using namespace geant4_app;

PrimaryGeneratorAction::PrimaryGeneratorAction() : G4VUserPrimaryGeneratorAction(), particleGun(1) {
    particleGun.SetParticleDefinition(G4ParticleTable::GetParticleTable()->FindParticle("e-"));
    particleGun.SetParticleEnergy(1.0 * MeV);
    particleGun.SetParticlePosition(G4ThreeVector(0.0, 0.0, 0.0));
    particleGun.SetParticleMomentumDirection(G4ThreeVector(0.0, 0.0, -1.0));
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) { particleGun.GeneratePrimaryVertex(event); }

void PrimaryGeneratorAction::SetEnergy(double energy) {
    auto ui = Application::GetUIManager();
    ui->ApplyCommand("/gun/energy " + to_string(energy) + " MeV");
}

void PrimaryGeneratorAction::SetPosition(const array<double, 3>& position) {
    auto ui = Application::GetUIManager();
    ui->ApplyCommand("/gun/position " + to_string(position[0]) + " " + to_string(position[1]) + " " +
                     to_string(position[2]) + " cm");
}

void PrimaryGeneratorAction::SetDirection(const array<double, 3>& direction) {
    auto ui = Application::GetUIManager();
    ui->ApplyCommand("/gun/direction " + to_string(direction[0]) + " " + to_string(direction[1]) + " " +
                     to_string(direction[2]));
}

void PrimaryGeneratorAction::SetParticle(const string& particle) {
    auto ui = Application::GetUIManager();
    ui->ApplyCommand("/gun/particle " + particle);
}
