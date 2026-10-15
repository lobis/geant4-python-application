
#include "geant4_application/PrimaryGeneratorAction.h"
#include "geant4_application/Application.h"

#include <G4Event.hh>
#include <G4Navigator.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTable.hh>
#include <G4PrimaryVertex.hh>
#include <G4RunManager.hh>
#include <G4SystemOfUnits.hh>
#include <G4Threading.hh>
#include <G4TransportationManager.hh>
#include <G4VSolid.hh>
#include <G4VUserPrimaryGeneratorAction.hh>
#include <G4Version.hh>

using namespace std;
using namespace geant4_app;

PrimaryGeneratorAction::PrimaryGeneratorAction() : G4VUserPrimaryGeneratorAction() {
#if G4VERSION_NUMBER >= 1140
    // Geant4 11.4 keeps the previous gun position, with only a warning, when a new
    // one is outside the world (and only after initialization). Accept every
    // position instead; GeneratePrimaries reports a vertex outside the world as an error.
    gun.CheckInside(false);
#endif
}


// Geant4 crashes (11.4: null dereference in G4SteppingManager::SetInitialStep)
// on a primary that starts outside the world. Generate no vertex instead, stop
// the run cleanly and let Application::Run report the error once BeamOn returns:
// throwing from here would leave the run manager in the middle of a run.
bool PrimaryGeneratorAction::RejectOutsideWorld(const G4ThreeVector& position) {
    const auto world = G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking()->GetWorldVolume();
    if (world == nullptr ||
        world->GetLogicalVolume()->GetSolid()->Inside(position - world->GetTranslation()) != kOutside) {
        return false;
    }
    {
        lock_guard<mutex> lock(pendingErrorMutex);
        if (pendingError.empty()) {
            pendingError = "Primary vertex at (" + to_string(position.x() / cm) + ", " + to_string(position.y() / cm) +
                           ", " + to_string(position.z() / cm) + ") cm is outside the world volume '" +
                           world->GetName() + "'";
        }
    }
    G4RunManager::GetRunManager()->AbortRun(true);
    return true;
}

void PrimaryGeneratorAction::ThrowPendingError() {
    lock_guard<mutex> lock(pendingErrorMutex);
    if (!pendingError.empty()) {
        const auto error = pendingError;
        pendingError.clear();
        throw runtime_error(error);
    }
}

string PrimaryGeneratorAction::pendingError;
mutex PrimaryGeneratorAction::pendingErrorMutex;

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) {
    if (!awkwardPrimaryEventOffsets.empty()) {
        const auto eventId = static_cast<size_t>(event->GetEventID());
        for (size_t i = awkwardPrimaryEventOffsets[eventId]; i < awkwardPrimaryEventOffsets[eventId + 1]; ++i) {
            if (!awkwardPrimaryEnergies.empty()) gun.SetParticleEnergy(awkwardPrimaryEnergies[i] * keV);
            if (!awkwardPrimaryPositions.empty()) {
                const auto& p = awkwardPrimaryPositions[i];
                gun.SetParticlePosition(G4ThreeVector(p[0] * cm, p[1] * cm, p[2] * cm));
            }
            if (!awkwardPrimaryDirections.empty()) {
                const auto& d = awkwardPrimaryDirections[i];
                gun.SetParticleMomentumDirection(G4ThreeVector(d[0], d[1], d[2]));
            }
            if (!awkwardPrimaryParticles.empty()) {
                auto* particle = G4ParticleTable::GetParticleTable()->FindParticle(awkwardPrimaryParticles[i]);
                if (particle == nullptr) throw runtime_error("Primary particle not found: " + awkwardPrimaryParticles[i]);
                gun.SetParticleDefinition(particle);
            }
            if (RejectOutsideWorld(gun.GetParticlePosition())) return;
            gun.GeneratePrimaryVertex(event);
        }
        return;
    }
    if (!awkwardPrimaryEnergies.empty()) {
        const double energy = awkwardPrimaryEnergies[event->GetEventID()];
        gun.SetParticleEnergy(energy * keV);
    }
    if (!awkwardPrimaryPositions.empty()) {
        const auto& position = awkwardPrimaryPositions[event->GetEventID()];
        gun.SetParticlePosition(G4ThreeVector(position[0] * cm, position[1] * cm, position[2] * cm));
    }
    if (!awkwardPrimaryDirections.empty()) {
        const auto& direction = awkwardPrimaryDirections[event->GetEventID()];
        gun.SetParticleMomentumDirection(G4ThreeVector(direction[0], direction[1], direction[2]));
    }
    if (!awkwardPrimaryParticles.empty()) {
        const auto& particleAwkward = awkwardPrimaryParticles[event->GetEventID()];
        auto* particle = G4ParticleTable::GetParticleTable()->FindParticle(particleAwkward);
        if (particle == nullptr) {
            throw runtime_error("PrimaryGeneratorAction::GeneratePrimaries - particle '" + particleAwkward + "' not found");
        }
        gun.SetParticleDefinition(particle);
    }

    if (generatorType == "gun") {
        if (RejectOutsideWorld(gun.GetParticlePosition())) return;
        gun.GeneratePrimaryVertex(event);
    } else if (generatorType == "gps") {
        gps.GeneratePrimaryVertex(event);
    } else {
        throw runtime_error("PrimaryGeneratorAction::GeneratePrimaries - generatorType must be 'gun', 'gps'");
    }
}

void PrimaryGeneratorAction::SetGeneratorType(const string& type) {
    const auto allowedTypes = set<string>({"gun", "gps"});
    if (allowedTypes.find(type) == allowedTypes.end()) {
        throw runtime_error("PrimaryGeneratorAction::SetGeneratorType - type must be 'gun' or 'gps'");
    }
    generatorType = type;
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

void PrimaryGeneratorAction::ClearAwkwardPrimaries() {
    awkwardPrimaryEnergies.clear();
    awkwardPrimaryPositions.clear();
    awkwardPrimaryDirections.clear();
    awkwardPrimaryParticles.clear();
    awkwardPrimaryEventOffsets.clear();
}

vector<double> PrimaryGeneratorAction::awkwardPrimaryEnergies = {};
vector<array<double, 3>> PrimaryGeneratorAction::awkwardPrimaryPositions = {};
vector<array<double, 3>> PrimaryGeneratorAction::awkwardPrimaryDirections = {};
vector<string> PrimaryGeneratorAction::awkwardPrimaryParticles = {};
vector<size_t> PrimaryGeneratorAction::awkwardPrimaryEventOffsets = {};
