
#include "geant4_application/PhysicsList.h"

#include <G4DecayPhysics.hh>
#include <G4EmExtraPhysics.hh>
#include <G4EmStandardPhysics.hh>
#include <G4EmStandardPhysics_option4.hh>
#include <G4HadronElasticPhysics.hh>
#include <G4HadronPhysicsFTFP_BERT.hh>
#include <G4IonPhysics.hh>
#include <G4NeutronTrackingCut.hh>
#include <G4OpticalPhysics.hh>
#include <G4RadioactiveDecayPhysics.hh>
#include <G4StoppingPhysics.hh>
#include <G4VModularPhysicsList.hh>

using namespace geant4_app;

PhysicsList::PhysicsList(bool optical) : G4VModularPhysicsList() {
    SetVerboseLevel(1);

    // Electromagnetic physics
    // RegisterPhysics(new G4EmStandardPhysics());
    // RegisterPhysics(new G4EmExtraPhysics());
    RegisterPhysics(new G4EmStandardPhysics_option4());

    // Decay physics
    RegisterPhysics(new G4DecayPhysics());

    // Radioactive decay. Must come after the EM constructor: registered first, it
    // creates the atomic de-excitation module and initializes it before the
    // material-cuts couples exist, which leaves fluorescence and Auger emission
    // off in every volume (while /process/em/printParameters reports them on).
    RegisterPhysics(new G4RadioactiveDecayPhysics());

    // Hadronic physics
    RegisterPhysics(new G4HadronElasticPhysics());
    RegisterPhysics(new G4HadronPhysicsFTFP_BERT());

    // Stopping physics
    RegisterPhysics(new G4StoppingPhysics());

    // Ion physics
    RegisterPhysics(new G4IonPhysics());

    // Neutron tracking cut
    RegisterPhysics(new G4NeutronTrackingCut());

    if (optical) {
        RegisterPhysics(new G4OpticalPhysics());
    }
}
