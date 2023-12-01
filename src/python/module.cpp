
#include <pybind11/pybind11.h>

#include "geant4/Application.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;
using namespace geant4_app;

PYBIND11_MODULE(_core, m) {
    m.doc() = R"pbdoc(
        Geant4 Python Application
        -------------------------
    )pbdoc";

    py::class_<Application>(m, "Application")
            .def(py::init<>())
            .def("setup_manager", &Application::SetupManager, py::arg("n_threads") = 0)
            .def("setup_detector", &Application::SetupDetector, py::arg("gdml"), py::arg("sensitive_volumes") = py::set())
            .def("setup_physics", &Application::SetupPhysics)
            .def("setup_action", &Application::SetupAction)
            .def("initialize", &Application::Initialize)
            .def("run", &Application::Run, py::arg("n_events") = 1)
            .def("is_setup", &Application::IsSetup)
            .def("is_initialized", &Application::IsInitialized)
            .def_property("random_seed", &Application::GetRandomSeed, &Application::SetRandomSeed)
            .def_static("command", &Application::Command, py::arg("command"))
            .def_static("list_commands", &Application::ListCommands, py::arg("directory") = "/")
            .def_static("start_gui", &Application::StartGUI)
            .def_property("generator", &Application::GetPrimaryGeneratorAction, nullptr, py::return_value_policy::reference_internal)
            .def_property("detector", &Application::GetDetectorConstruction, nullptr, py::return_value_policy::reference_internal)
            .def_property("stacking", &Application::GetStackingAction, nullptr, py::return_value_policy::reference_internal);

    py::class_<PrimaryGeneratorAction>(m, "PrimaryGeneratorAction")
            .def_static("set_energy", &PrimaryGeneratorAction::SetEnergy, py::arg("energy"))
            .def_static("set_position", &PrimaryGeneratorAction::SetPosition, py::arg("position"))
            .def_static("set_direction", &PrimaryGeneratorAction::SetDirection, py::arg("direction"))
            .def_static("set_particle", &PrimaryGeneratorAction::SetParticle, py::arg("particle"));

    py::class_<DetectorConstruction>(m, "DetectorConstruction")
            .def("check_overlaps", &DetectorConstruction::CheckOverlaps)
            .def_static("print_materials", &DetectorConstruction::PrintMaterials)
            // why are properties not working (due to sets?)
            .def_property("materials", &DetectorConstruction::GetMaterialNames, nullptr)
            .def_static("get_materials", &DetectorConstruction::GetMaterialNames)
            .def_property("logical_volumes", &DetectorConstruction::GetLogicalVolumeNames, nullptr)
            .def_static("get_logical_volumes", &DetectorConstruction::GetLogicalVolumeNames)
            .def_property("physical_volumes", &DetectorConstruction::GetPhysicalVolumeNames, nullptr)
            .def_static("get_physical_volumes", &DetectorConstruction::GetPhysicalVolumeNames);

    py::class_<StackingAction>(m, "StackingAction")
            .def_property("ignored_particles", &StackingAction::GetIgnoredParticles, &StackingAction::SetIgnoredParticles)
            .def_static("get_ignored_particles", &StackingAction::GetIgnoredParticles)
            .def_static("ignore_particle", &StackingAction::IgnoreParticle, py::arg("name"))
            .def_static("ignore_particle_undo", &StackingAction::IgnoreParticleUndo, py::arg("name"));

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
