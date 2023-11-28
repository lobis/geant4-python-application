#include "geant4/DetectorConstruction.h"

#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4NistManager.hh"
#include "G4PVPlacement.hh"
#include "G4VisAttributes.hh"

DetectorConstruction::DetectorConstruction() : G4VUserDetectorConstruction() {}

G4VPhysicalVolume* DetectorConstruction::Construct() {
    // World
    G4double world_size = 10.0;// Half size of world
    G4Box* solidWorld = new G4Box("World", world_size, world_size, world_size);
    G4LogicalVolume* logicWorld =
            new G4LogicalVolume(solidWorld, G4NistManager::Instance()->FindOrBuildMaterial("G4_AIR"), "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0);

    // Detector
    G4double detector_size = 1.0;// Half size of detector
    G4Box* solidDetector = new G4Box("Detector", detector_size, detector_size, detector_size);
    G4LogicalVolume* logicDetector = new G4LogicalVolume(
            solidDetector, G4NistManager::Instance()->FindOrBuildMaterial("G4_WATER"), "Detector");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 0), logicDetector, "Detector", logicWorld, false, 0);

    // Visualization attributes
    G4VisAttributes* detectorVisAtt = new G4VisAttributes(G4Colour(0.0, 1.0, 0.0));// Green
    logicDetector->SetVisAttributes(detectorVisAtt);

    return physWorld;
}
