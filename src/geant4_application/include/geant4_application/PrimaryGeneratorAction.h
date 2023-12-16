
#pragma once

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>

#include <G4GeneralParticleSource.hh>
#include <G4ParticleGun.hh>
#include <G4VUserPrimaryGeneratorAction.hh>

namespace py = pybind11;

namespace geant4_app {

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction {
public:
    PrimaryGeneratorAction();

    void GeneratePrimaries(G4Event*) override;

    static void SetEnergy(double energy);
    static void SetPosition(const std::array<double, 3>& position);
    static void SetDirection(const std::array<double, 3>& direction);
    static void SetParticle(const std::string& particle);

    static std::string GetGeneratorType() { return generatorType; }
    static void SetGeneratorType(const std::string& generatorType);

    inline static void SetAwkwardPrimaryEnergies(const std::vector<double>& energies) { awkwardPrimaryEnergies = energies; }
    inline static void SetAwkwardPrimaryPositions(const std::vector<std::array<double, 3>>& positions) { awkwardPrimaryPositions = positions; }
    inline static void SetAwkwardPrimaryDirections(const std::vector<std::array<double, 3>>& directions) { awkwardPrimaryDirections = directions; }
    inline static void SetAwkwardPrimaryParticles(const std::vector<std::string>& particles) { awkwardPrimaryParticles = particles; }
    static void ClearAwkwardPrimaries();

private:
    G4ParticleGun gun;
    G4GeneralParticleSource gps;
    static std::string generatorType;

    static std::vector<double> awkwardPrimaryEnergies;
    static std::vector<std::array<double, 3>> awkwardPrimaryPositions;
    static std::vector<std::array<double, 3>> awkwardPrimaryDirections;
    static std::vector<std::string> awkwardPrimaryParticles;
};

}// namespace geant4_app
