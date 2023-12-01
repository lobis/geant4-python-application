
#ifndef GEANT4_APPLICATION_PHYSICSLIST_H
#define GEANT4_APPLICATION_PHYSICSLIST_H

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

namespace geant4_app {

class PhysicsList : public G4VModularPhysicsList {
public:
    PhysicsList();
};
}// namespace geant4_app
#endif// GEANT4_APPLICATION_PHYSICSLIST_H
