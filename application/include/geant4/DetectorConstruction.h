
#ifndef GEANT4_APPLICATION_DETECTORCONSTRUCTION_H
#define GEANT4_APPLICATION_DETECTORCONSTRUCTION_H

#include <G4GDMLParser.hh>
#include <G4VUserDetectorConstruction.hh>
#include <globals.hh>

using namespace std;

class G4VPhysicalVolume;

class DetectorConstruction : public G4VUserDetectorConstruction {

public:
    explicit DetectorConstruction(std::string gdml);
    G4VPhysicalVolume* Construct() override;
    G4VPhysicalVolume* GetWorld() const { return world; }

private:
    std::string gdml;
    G4VPhysicalVolume* world;
};

#endif// GEANT4_APPLICATION_DETECTORCONSTRUCTION_H
