
#pragma once

#include <G4ParticleGun.hh>
#include <G4VUserPrimaryGeneratorAction.hh>

namespace geant4_app {

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction {
public:
    PrimaryGeneratorAction();

    G4ParticleGun particleGun;

    void GeneratePrimaries(G4Event*) override;

    static void SetEnergy(double energy);
    static void SetPosition(const std::array<double, 3>& position);
    static void SetDirection(const std::array<double, 3>& direction);
    static void SetParticle(const std::string& particle);
};

}// namespace geant4_app
