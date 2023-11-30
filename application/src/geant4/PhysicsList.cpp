
#include "geant4/PhysicsList.h"

#include <G4DecayPhysics.hh>
#include <G4EmExtraPhysics.hh>
#include <G4EmStandardPhysics.hh>
#include <G4EmStandardPhysics_option4.hh>
#include <G4HadronElasticPhysics.hh>
#include <G4HadronPhysicsFTFP_BERT.hh>
#include <G4IonPhysics.hh>
#include <G4NeutronTrackingCut.hh>
#include <G4RadioactiveDecayPhysics.hh>
#include <G4StoppingPhysics.hh>
#include <G4VModularPhysicsList.hh>

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
