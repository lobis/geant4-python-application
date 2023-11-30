//
// Created by Luis Antonio Obis Aparicio on 25/11/23.
//

#ifndef GEANT4_APPLICATION_PRIMARYGENERATORACTION_H
#define GEANT4_APPLICATION_PRIMARYGENERATORACTION_H

#include <G4ParticleGun.hh>
#include <G4VUserPrimaryGeneratorAction.hh>

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

#endif// GEANT4_APPLICATION_PRIMARYGENERATORACTION_H
