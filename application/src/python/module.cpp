
#include "geant4/Application.h"

#include "pybind11/pybind11.h"

using namespace geant4;
namespace py = pybind11;

void init_Application(py::module& m) {
    py::class_<Application>(m, "Application")
            .def(py::init<>())
            .def("setup_manager", &Application::SetupManager, py::arg("n_threads") = 0)
            .def("setup_detector", &Application::SetupDetector<std::string, std::set<std::string>>, py::arg("gdml"), py::arg("sensitive_volumes") = py::set())
            .def("setup_physics", &Application::SetupPhysics)
            .def("setup_action", &Application::SetupAction)
            .def("initialize", &Application::Initialize)
            .def("run", &Application::Run, py::arg("n_events") = 1)
            .def("is_setup", &Application::IsSetup)
            .def("is_initialized", &Application::IsInitialized);
}

PYBIND11_MODULE(geant4, m) {
    init_Application(m);
}
