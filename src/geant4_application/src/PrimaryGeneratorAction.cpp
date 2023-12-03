
#include "geant4_application/PrimaryGeneratorAction.h"
#include "geant4_application/Application.h"

#include <G4Event.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTable.hh>
#include <G4RunManager.hh>
#include <G4SystemOfUnits.hh>
#include <G4Threading.hh>
#include <G4VUserPrimaryGeneratorAction.hh>

using namespace std;
using namespace geant4_app;

PrimaryGeneratorAction::PrimaryGeneratorAction() : G4VUserPrimaryGeneratorAction() {}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) {
    if (generatorType == "python") {
        lock_guard<mutex> lock(pythonMutex);
        auto result = pythonGenerator();
        cout << "PrimaryGeneratorAction::GeneratePrimaries - result: " << result << endl;
        throw runtime_error("PrimaryGeneratorAction::GeneratePrimaries - pythonGenerator not implemented");
    } else if (generatorType == "gun") {
        gun.GeneratePrimaryVertex(event);
    } else if (generatorType == "gps") {
        gps.GeneratePrimaryVertex(event);
    } else {
        throw runtime_error("PrimaryGeneratorAction::GeneratePrimaries - generatorType must be 'gun', 'gps', or 'python'");
    }
}

void PrimaryGeneratorAction::SetGeneratorType(const string& type) {
    if (!set<string>({"gun", "gps", "python"}).contains(type)) {
        throw runtime_error("PrimaryGeneratorAction::SetGeneratorType - type must be 'gun', 'gps', or 'python'");
    }
    generatorType = type;
}

void PrimaryGeneratorAction::SetPythonGenerator(const py::function& generator) {
    lock_guard<mutex> lock(pythonMutex);
    pythonGenerator = generator;
    SetGeneratorType("python");
}

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

string PrimaryGeneratorAction::generatorType = "gun";
py::function PrimaryGeneratorAction::pythonGenerator = py::function();
