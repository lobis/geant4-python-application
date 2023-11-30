
#include "geant4/Application.h"

#include "pybind11/chrono.h"
#include "pybind11/complex.h"
#include "pybind11/functional.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

using namespace geant4;
namespace py = pybind11;

constexpr const char* basicGdml = R"(
<?xml version="1.0" encoding="utf-8" standalone="no" ?>

<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">

    <define>
        <constant name="worldSize" value="1000"/>
        <constant name="boxSize" value="500"/>
    </define>

    <solids>
        <box name="WorldSolid" x="worldSize" y="worldSize" z="worldSize" lunit="mm"/>
        <box name="boxSolid" x="boxSize" y="boxSize" z="boxSize" lunit="mm"/>
    </solids>

    <structure>
        <volume name="boxVolume">
            <materialref ref="G4_WATER"/>
            <solidref ref="boxSolid"/>
        </volume>

        <volume name="World">
            <materialref ref="G4_AIR"/>
            <solidref ref="WorldSolid"/>

            <physvol name="box">
                <volumeref ref="boxVolume"/>
                <position name="boxPosition" unit="mm" x="0" y="0" z="0"/>
            </physvol>

        </volume>
    </structure>

    <setup name="Default" version="1.0">
        <world ref="World"/>
    </setup>
</gdml>
)";

void init_Application(py::module& m) {
    py::class_<Application>(m, "Application")
            .def(py::init<>())
            .def("setup_manager", &Application::SetupManager, py::arg("n_threads") = 0)
            .def("setup_detector", &Application::SetupDetector, py::arg("gdml") = basicGdml, py::arg("sensitive_volumes") = py::set())
            .def("setup_physics", &Application::SetupPhysics)
            .def("setup_action", &Application::SetupAction)
            .def("initialize", &Application::Initialize)
            .def("run", &Application::Run, py::arg("n_events") = 1)
            .def("is_setup", &Application::IsSetup)
            .def("is_initialized", &Application::IsInitialized)
            .def_property("random_seed", &Application::GetRandomSeed, &Application::SetRandomSeed)
            .def_static("command", &Application::Command, py::arg("command"))
            .def_static("list_commands", &Application::ListCommands, py::arg("directory") = "/")
            .def_property("primary_generator", &Application::GetPrimaryGeneratorAction, nullptr, py::return_value_policy::reference_internal);

    py::class_<PrimaryGeneratorAction>(m, "PrimaryGenerator")
            .def(py::init<>())
            .def_static("set_energy", &PrimaryGeneratorAction::SetEnergy, py::arg("energy"))
            .def_static("set_position", &PrimaryGeneratorAction::SetPosition, py::arg("position"))
            .def_static("set_direction", &PrimaryGeneratorAction::SetDirection, py::arg("direction"))
            .def_static("set_particle", &PrimaryGeneratorAction::SetParticle, py::arg("particle"));
}

PYBIND11_MODULE(geant4_cpp, m) {
    init_Application(m);
}
