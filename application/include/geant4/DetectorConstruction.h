
#ifndef GEANT4_APPLICATION_DETECTORCONSTRUCTION_H
#define GEANT4_APPLICATION_DETECTORCONSTRUCTION_H

#include <G4VUserDetectorConstruction.hh>
#include <globals.hh>

using namespace std;

class G4VPhysicalVolume;

class DetectorConstruction : public G4VUserDetectorConstruction {
public:
    DetectorConstruction();
    G4VPhysicalVolume* Construct() override;

private:
    G4VPhysicalVolume* fWorld;
};

#endif// GEANT4_APPLICATION_DETECTORCONSTRUCTION_H
