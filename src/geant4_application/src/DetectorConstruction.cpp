
#include "geant4_application/DetectorConstruction.h"
#include "geant4_application/Application.h"
#include "geant4_application/SensitiveDetector.h"

#include <G4LogicalVolumeStore.hh>
#include <G4NistManager.hh>
#include <G4PhysicalVolumeStore.hh>

#include <filesystem>
#include <random>

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

    const auto gdmlTemporaryDir = Application::GetTemporaryApplicationDirectory() / "gdml";
    if (!fs::exists(gdmlTemporaryDir)) {
        fs::create_directories(gdmlTemporaryDir);
    }

    // get a unique id for the temporary file. This should be unique across all processes (batch jobs)
    auto uniqueString = std::to_string(std::hash<unsigned int>{}(std::random_device()()));
    const auto gdmlTmpPath = gdmlTemporaryDir / ("GDML_" + uniqueString + ".gdml");
    cout << "Writing temporary GDML file to " << gdmlTmpPath << endl;
    // write contents of gdml string into file, raise exception if there is a problem
    ofstream gdmlTmpFile(gdmlTmpPath);
    if (!gdmlTmpFile.is_open()) {
        throw runtime_error("Could not open temporary GDML file");
    }
    gdmlTmpFile << gdml;
    gdmlTmpFile.close();
    gdml = "";// clear gdml string to save memory

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

set<string> DetectorConstruction::GetNISTMaterialNames() {
    set<string> names;
    const auto materialTable = G4NistManager::Instance()->GetNistMaterialNames();
    for (const auto& material: materialTable) {
        names.insert(material);
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

set<string> DetectorConstruction::GetPhysicalVolumesFromLogicalVolume(const string& logicalVolumeName) {
    set<string> names;
    const auto logicalVolume = G4LogicalVolumeStore::GetInstance()->GetVolume(logicalVolumeName, false);
    if (logicalVolume == nullptr) {
        throw runtime_error("Could not find logical volume '" + logicalVolumeName + "'");
    }
    const auto physicalVolumeTable = G4PhysicalVolumeStore::GetInstance();
    for (const auto& physicalVolume: *physicalVolumeTable) {
        if (physicalVolume->GetLogicalVolume() == logicalVolume) {
            names.insert(physicalVolume->GetName());
        }
    }
    if (names.empty()) {
        throw runtime_error("Could not find physical volumes for logical volume '" + logicalVolumeName + "'");
    }
    return names;
}

string DetectorConstruction::GetLogicalVolumeFromPhysicalVolume(const string& physicalVolumeName) {
    const auto physicalVolume = G4PhysicalVolumeStore::GetInstance()->GetVolume(physicalVolumeName, false);
    if (physicalVolume == nullptr) {
        throw runtime_error("Could not find physical volume '" + physicalVolumeName + "'");
    }
    const auto logicalVolume = physicalVolume->GetLogicalVolume();
    if (logicalVolume == nullptr) {
        throw runtime_error("Could not find logical volume for physical volume '" + physicalVolumeName + "'");
    }
    return logicalVolume->GetName();
}

string DetectorConstruction::GetMaterialFromVolume(const string& volumeName) {
    const auto physicalVolume = G4PhysicalVolumeStore::GetInstance()->GetVolume(volumeName, false);
    const auto logicalVolume = G4LogicalVolumeStore::GetInstance()->GetVolume(volumeName, false);
    if (logicalVolume == nullptr && physicalVolume == nullptr) {
        throw runtime_error("Could not find volume '" + volumeName + "'");
    }
    if (logicalVolume != nullptr && physicalVolume != nullptr) {
        // not sure if this is possible, maybe instead of a runtime_error we should just return the material of the logical volume
        throw runtime_error("Volume '" + volumeName + "' is both a logical and physical volume");
    }

    const G4Material* material;
    if (logicalVolume != nullptr) {
        material = logicalVolume->GetMaterial();
    } else {
        material = physicalVolume->GetLogicalVolume()->GetMaterial();
    }

    if (material == nullptr) {
        throw runtime_error("Could not find material for logical volume '" + logicalVolume->GetName() + "'");
    }

    return material->GetName();
}
