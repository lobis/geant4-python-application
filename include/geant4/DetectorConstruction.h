
#pragma once

#include <G4GDMLParser.hh>
#include <G4LogicalVolume.hh>
#include <G4LogicalVolumeStore.hh>
#include <G4NistManager.hh>
#include <G4PhysicalVolumeStore.hh>
#include <G4VUserDetectorConstruction.hh>
#include <G4VisAttributes.hh>
#include <globals.hh>

namespace geant4_app {

class DetectorConstruction : public G4VUserDetectorConstruction {

public:
    DetectorConstruction(std::string gdml, const std::set<std::string>& sensitiveVolumes = {});
    G4VPhysicalVolume* Construct() override;
    G4VPhysicalVolume* GetWorld() const { return world; }

    bool CheckOverlaps() const;
    void ConstructSDandField() override;

    static void PrintMaterials();
    static std::set<std::string> GetMaterialNames();
    static std::set<std::string> GetLogicalVolumeNames();
    static std::set<std::string> GetPhysicalVolumeNames();

private:
    std::string gdml;
    G4VPhysicalVolume* world = nullptr;

    std::set<std::string> sensitiveVolumes;
};

}// namespace geant4_app
