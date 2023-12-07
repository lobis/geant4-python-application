
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/SensitiveDetector.h"

#include <G4LogicalVolumeStore.hh>
#include <G4NistManager.hh>
#include <G4PhysicalVolumeStore.hh>
#include <G4VisAttributes.hh>

#include <filesystem>
#include <unistd.h>

using namespace std;
using namespace geant4_app;
namespace fs = std::filesystem;

DetectorConstruction::DetectorConstruction(const string& gdml) : G4VUserDetectorConstruction() {
    SetGDML(gdml);
    // TODO: store this string as compressed data?
}

void DetectorConstruction::SetGDML(const string& gdmlContents) {
    // Remove leading characters from gdml string, otherwise GDML parser will fail
    if (IsConstructed()) {
        throw runtime_error("Detector is already constructed");
    }
    gdml = gdmlContents;
    gdml.erase(0, this->gdml.find_first_not_of(" \n\r\t"));
}

void DetectorConstruction::SetSensitiveVolumes(const set<string>& volumes) {
    if (sensitiveDetectorConstructed) {
        throw runtime_error("Sensitive volumes cannot be set after sensitive detector construction");
    }
    sensitiveVolumes = volumes;
}

G4VPhysicalVolume* DetectorConstruction::Construct() {
    G4GDMLParser parser;

    auto gdmlTmpPath = filesystem::temp_directory_path() / ("GDML_PID" + to_string(getpid()) + ".gdml");
    // write contents of gdml string into file, raise exception if there is a problem
    ofstream gdmlTmpFile(gdmlTmpPath);
    if (!gdmlTmpFile.is_open()) {
        throw runtime_error("Could not open temporary GDML file");
    }
    gdmlTmpFile << gdml;
    gdmlTmpFile.close();

    parser.Read(gdmlTmpPath.string(), false);
    // we are storing a copy of the gdml string!

    // TODO: improve cleanup. Is it necessary to write a temporary file?
    filesystem::remove(gdmlTmpPath);

    world = parser.GetWorldVolume();
    if (world == nullptr) {
        throw runtime_error("Error constructing world volume from GDML");
    }
    return world;
}

bool DetectorConstruction::CheckOverlaps() const {
    if (!IsConstructed()) {
        throw runtime_error("Detector is not constructed");
    }
    return world->CheckOverlaps();
}

void DetectorConstruction::ConstructSDandField() {
    for (const auto& volumeName: sensitiveVolumes) {
        auto sensitiveDetector = new SensitiveDetector(volumeName);

        // TODO: Support physical volumes too
        auto logicalVolume = G4LogicalVolumeStore::GetInstance()->GetVolume(volumeName, false);
        if (logicalVolume == nullptr) {
            throw runtime_error("Could not find logical volume '" + volumeName + "'");
        }

        logicalVolume->SetSensitiveDetector(sensitiveDetector);
        // TODO: Regions
    }
    sensitiveDetectorConstructed = true;
}

set<string> DetectorConstruction::GetMaterialNames() {
    set<string> names;
    const auto materialTable = G4Material::GetMaterialTable();
    for (const auto& material: *materialTable) {
        names.insert(material->GetName());
    }
    return names;
}

set<string> DetectorConstruction::GetLogicalVolumeNames() {
    set<string> names;
    const auto logicalVolumeTable = G4LogicalVolumeStore::GetInstance();
    for (const auto& logicalVolume: *logicalVolumeTable) {
        names.insert(logicalVolume->GetName());
    }
    return names;
}

set<string> DetectorConstruction::GetPhysicalVolumeNames() {
    set<string> names;
    const auto physicalVolumeTable = G4PhysicalVolumeStore::GetInstance();
    for (const auto& physicalVolume: *physicalVolumeTable) {
        names.insert(physicalVolume->GetName());
    }
    return names;
}
