
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
    DetectorConstruction(const std::string& gdml);
    G4VPhysicalVolume* Construct() override;
    G4VPhysicalVolume* GetWorld() const { return world; }

    bool CheckOverlaps() const;
    void ConstructSDandField() override;

    void SetSensitiveVolumes(const std::set<std::string>& sensitiveVolumes);
    std::set<std::string> GetSensitiveVolumes() const { return sensitiveVolumes; }

    std::string GetGDML() const { return gdml; }
    void SetGDML(const std::string& gdml);

    static std::set<std::string> GetMaterialNames();
    static std::set<std::string> GetNISTMaterialNames();
    static std::set<std::string> GetLogicalVolumeNames();
    static std::set<std::string> GetPhysicalVolumeNames();

    static std::set<std::string> GetPhysicalVolumesFromLogicalVolume(const std::string& logicalVolumeName);
    static std::string GetLogicalVolumeFromPhysicalVolume(const std::string& physicalVolumeName);
    static std::string GetMaterialFromVolume(const std::string& volumeName);

    bool IsConstructed() const { return world != nullptr; }

private:
    std::string gdml;
    G4VPhysicalVolume* world = nullptr;

    std::set<std::string> sensitiveVolumes;
    bool sensitiveDetectorConstructed = false;
};

}// namespace geant4_app
