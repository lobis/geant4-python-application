
#ifndef GEANT4_APPLICATION_DETECTORCONSTRUCTION_H
#define GEANT4_APPLICATION_DETECTORCONSTRUCTION_H

#include <G4GDMLParser.hh>
#include <G4VUserDetectorConstruction.hh>
#include <globals.hh>

using namespace std;

class G4VPhysicalVolume;

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

#endif// GEANT4_APPLICATION_DETECTORCONSTRUCTION_H
