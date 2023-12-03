
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

    static py::function GetPythonGenerator() { return pythonGenerator; }
    void SetPythonGenerator(const py::function& pythonGenerator);

private:
    G4ParticleGun gun;
    G4GeneralParticleSource gps;
    static py::function pythonGenerator;
    std::mutex pythonMutex;
    static std::string generatorType;
};

}// namespace geant4_app
