#include <utility>

#include "geant4/DetectorConstruction.h"
#include "geant4/SensitiveDetector.h"

#include <G4LogicalVolume.hh>
#include <G4LogicalVolumeStore.hh>
#include <G4NistManager.hh>
#include <G4PhysicalVolumeStore.hh>
#include <G4VisAttributes.hh>

#include <filesystem>
#include <unistd.h>

using namespace std;
using namespace geant4_app;
namespace fs = std::filesystem;

DetectorConstruction::DetectorConstruction(string gdml, const std::set<std::string>& sensitiveVolumes) : G4VUserDetectorConstruction(), gdml(std::move(gdml)), sensitiveVolumes(sensitiveVolumes) {
    // Remove leading characters from gdml string, otherwise GDML parser will fail
    this->gdml.erase(0, this->gdml.find_first_not_of(" \n\r\t"));
    // TODO: store this string as compressed data?
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
    gdml.clear();

    // TODO: improve cleanup. Is it necessary to write a temporary file?
    filesystem::remove(gdmlTmpPath);


    world = parser.GetWorldVolume();
    return world;
}

bool DetectorConstruction::CheckOverlaps() const {
    return world->CheckOverlaps();
}

void DetectorConstruction::ConstructSDandField() {

    for (const auto& volumeName: sensitiveVolumes) {
        auto sensitiveDetector = new SensitiveDetector(volumeName);

        // TODO: Support physical volumes too
        auto logicalVolume = G4LogicalVolumeStore::GetInstance()->GetVolume(volumeName, false);
        if (logicalVolume == nullptr) {
            throw runtime_error("Could not find logical volume " + volumeName);
        }

        logicalVolume->SetSensitiveDetector(sensitiveDetector);
        // TODO: Regions
    }
}

void DetectorConstruction::PrintMaterials() {
    const auto materialTable = G4Material::GetMaterialTable();
    for (const auto& material: *materialTable) {
        cout << material->GetName() << ", " << material->GetDensity() << endl;
    }
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
