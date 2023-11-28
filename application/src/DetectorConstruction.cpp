#include <utility>

#include "geant4/DetectorConstruction.h"

#include "G4LogicalVolume.hh"
#include "G4NistManager.hh"
#include "G4VisAttributes.hh"
#include "filesystem"
#include <unistd.h>

using namespace std;
namespace fs = std::filesystem;

DetectorConstruction::DetectorConstruction(string gdml) : G4VUserDetectorConstruction(), gdml(std::move(gdml)) {
    // Need to remove leading characters from gdml string, otherwise GDML parser will fail
    this->gdml.erase(0, this->gdml.find_first_not_of(" \n\r\t"));
    // TODO: store this string as compressed data
}

G4VPhysicalVolume* DetectorConstruction::Construct() {
    G4GDMLParser parser;

    auto gdmlTmpPath = filesystem::temp_directory_path() / ("GDML" + to_string(getpid()) + ".gdml");
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
