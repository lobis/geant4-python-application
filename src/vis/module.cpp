// The interactive Qt viewer, built as its own extension module so that only
// calling Application.visualize() loads Qt; importing the package never does.
// It drives the Geant4 instance set up by _geant4_application through Geant4's
// singleton managers, which both modules share via the shared Geant4 libraries.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <G4RunManager.hh>
#include <G4UIExecutive.hh>
#include <G4UImanager.hh>
#include <G4VisExecutive.hh>

#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace py = pybind11;

namespace {

void StartVisualization(const std::vector<std::string>& commands) {
    if (G4RunManager::GetRunManager() == nullptr) {
        throw std::runtime_error("Geant4 run manager is not set up; start the Application first");
    }

    int argc = 1;
    char applicationName[] = "geant4-python-application";
    char* argv[] = {applicationName, nullptr};

    auto visualization = std::make_unique<G4VisExecutive>();
    visualization->Initialize();

    auto ui = std::make_unique<G4UIExecutive>(argc, argv, "qt");
    auto* uiManager = G4UImanager::GetUIpointer();
    for (const auto& command: commands) {
        const int code = uiManager->ApplyCommand(command);
        if (code != 0) {
            throw std::runtime_error("Command '" + command + "' failed with code " + std::to_string(code));
        }
    }
    ui->SessionStart();
}

}// namespace

PYBIND11_MODULE(_geant4_vis, m) {
    m.doc() = "Interactive Geant4 Qt viewer for geant4_python_application";
    m.def("start_visualization", &StartVisualization, py::arg("commands"),
          "Open the Qt viewer and block until its window is closed.");
}
