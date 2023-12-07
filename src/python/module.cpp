
#include <pybind11/pybind11.h>

#include "geant4_application/Application.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;
using namespace geant4_app;
using namespace std;

PYBIND11_MODULE(_geant4_application, m) {
    m.doc() = R"pbdoc(
        Geant4 Python Application
        -------------------------
    )pbdoc";

    py::class_<Application>(m, "Application")
            .def(py::init<>())
            .def("setup_manager", &Application::SetupManager, py::arg("n_threads"))
            .def("setup_detector", &Application::SetupDetector, py::arg("gdml"))
            .def("setup_physics", &Application::SetupPhysics)
            .def("setup_action", &Application::SetupAction)
            .def("initialize", &Application::Initialize)
            .def("run", &Application::Run, py::arg("n_events"))
            .def("is_setup", &Application::IsSetup)
            .def("is_initialized", &Application::IsInitialized)
            .def("get_seed", &Application::GetRandomSeed)
            .def("set_seed", &Application::SetRandomSeed)
            .def_static("command", &Application::Command, py::arg("command"))
            .def_static("list_commands", &Application::ListCommands, py::arg("directory") = "/")
            .def_property_readonly("generator", &Application::GetPrimaryGeneratorAction, py::return_value_policy::reference_internal)
            .def_property_readonly("detector", &Application::GetDetectorConstruction, py::return_value_policy::reference_internal)
            .def_property_readonly("stacking", &Application::GetStackingAction, py::return_value_policy::reference_internal);

    py::class_<PrimaryGeneratorAction>(m, "PrimaryGeneratorAction")
            .def_property_static(
                    "type",
                    [](const py::object&) { return PrimaryGeneratorAction::GetGeneratorType(); },
                    [](const py::object&, const string& type) {
                        return PrimaryGeneratorAction::SetGeneratorType(type);
                    })
            // TODO
            .def_property_static(
                    "function",
                    [](const py::object&) { return PrimaryGeneratorAction::GetPythonGenerator(); },
                    nullptr)
            .def("set_function", &PrimaryGeneratorAction::SetPythonGenerator, py::arg("function"))
            .def_static("set_energy", &PrimaryGeneratorAction::SetEnergy, py::arg("energy"))
            .def_static("set_position", &PrimaryGeneratorAction::SetPosition, py::arg("position"))
            .def_static("set_direction", &PrimaryGeneratorAction::SetDirection, py::arg("direction"))
            .def_static("set_particle", &PrimaryGeneratorAction::SetParticle, py::arg("particle"));

    py::class_<DetectorConstruction>(m, "DetectorConstruction")
            .def("check_overlaps", &DetectorConstruction::CheckOverlaps)
            .def_static("get_materials", &DetectorConstruction::GetMaterialNames)
            .def_static("get_logical_volumes", &DetectorConstruction::GetLogicalVolumeNames)
            .def_static("get_physical_volumes", &DetectorConstruction::GetPhysicalVolumeNames)
            .def("get_sensitive_volumes", &DetectorConstruction::GetSensitiveVolumes)
            .def("set_sensitive_volumes", &DetectorConstruction::SetSensitiveVolumes, py::arg("volumes"))
            .def("get_gdml", &DetectorConstruction::GetGDML);


    py::class_<StackingAction>(m, "StackingAction")
            .def_property_static(
                    "particles_to_ignore",
                    [](const py::object&) { return StackingAction::GetParticlesToIgnore(); },
                    [](const py::object&, const set<string>& particles) { return StackingAction::SetParticlesToIgnore(particles); });

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
    m.attr("__geant4_version__") = MACRO_STRINGIFY(GEANT4_VERSION);
    m.attr("__awkward_version__") = MACRO_STRINGIFY(AWKWARD_VERSION);
    m.attr("__pybind11_version__") = MACRO_STRINGIFY(PYBIND11_VERSION);
}
