
#include "geant4_application/PhysicsList.h"

#include <G4Box.hh>
#include <G4DecayPhysics.hh>
#include <G4EmExtraPhysics.hh>
#include <G4EmStandardPhysics.hh>
#include <G4EmStandardPhysics_option4.hh>
#include <G4HadronElasticPhysics.hh>
#include <G4HadronElasticPhysicsHP.hh>
#include <G4HadronPhysicsFTFP_BERT.hh>
#include <G4HadronPhysicsQGSP_BIC_HP.hh>
#include <G4HadronicProcessStore.hh>
#include <G4IonPhysics.hh>
#include <G4Neutron.hh>
#include <G4NeutronTrackingCut.hh>
#include <G4NistManager.hh>
#include <G4PVPlacement.hh>
#include <G4ProcessTable.hh>
#include <G4ProcessTableMessenger.hh>
#include <G4RadioactiveDecayPhysics.hh>
#include <G4StoppingPhysics.hh>
#include <G4SystemOfUnits.hh>
#include <G4VModularPhysicsList.hh>
#include <G4VUserDetectorConstruction.hh>
#include <QBBC.hh>

using namespace geant4_app;

PhysicsList::PhysicsList() : G4VModularPhysicsList() {
    SetVerboseLevel(1);

    // Decay physics
    RegisterPhysics(new G4DecayPhysics());

    // Radioactive decay
    RegisterPhysics(new G4RadioactiveDecayPhysics());

    // Electromagnetic physics
    // RegisterPhysics(new G4EmStandardPhysics());
    // RegisterPhysics(new G4EmExtraPhysics());
    RegisterPhysics(new G4EmStandardPhysics_option4());

    // Hadronic physics
    RegisterPhysics(new G4HadronElasticPhysics());
    RegisterPhysics(new G4HadronPhysicsFTFP_BERT());

    // Stopping physics
    RegisterPhysics(new G4StoppingPhysics());

    // Ion physics
    RegisterPhysics(new G4IonPhysics());

    // Neutron tracking cut
    RegisterPhysics(new G4NeutronTrackingCut());
}

std::set<std::string> PhysicsList::GetPhysicsListNames() {
    std::set<std::string> names;
    // TODO
    return names;
}

std::set<std::string> PhysicsList::GetProcessNames() {
    std::set<std::string> names;
    // TODO
    return names;
}
