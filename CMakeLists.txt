cmake_minimum_required(VERSION 3.25...3.30)
# CMP0169 only exists from CMake 3.30; older versions already behave as OLD.
if (POLICY CMP0169)
    cmake_policy(SET CMP0169 OLD)
endif ()

set(CMAKE_CXX_STANDARD 17)
set(AWKWARD_VERSION "v2.6.8")
set(PYBIND11_VERSION "v2.13.6")

if (NOT DEFINED SKBUILD_PROJECT_NAME)
    # IDE
    set(SKBUILD_PROJECT_NAME geant4-python-application)
endif ()

project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYTHON_MODULE_NAME _geant4_application)
set(VIS_MODULE_NAME _geant4_vis)
option(GEANT4_PYTHON_APPLICATION_VISUALIZATION
       "Build the interactive Geant4 Qt viewer as a separate, lazily imported module" OFF)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(
    Python
    COMPONENTS Interpreter Development.Module
    REQUIRED)

if (GEANT4_PYTHON_APPLICATION_VISUALIZATION)
    # The viewer module and the physics module must share one Geant4 (its
    # managers are singletons), which only works with shared libraries.
    find_package(
        Geant4 11.2.2 CONFIG REQUIRED
        COMPONENTS gdml ui_all vis_all)
    if (NOT Geant4_shared_FOUND)
        message(FATAL_ERROR
                "GEANT4_PYTHON_APPLICATION_VISUALIZATION requires Geant4 built with shared libraries")
    endif ()
else ()
    # "static" is optional: Geant4Config fails if it is required but only shared
    # libraries are installed, while as an optional component it still selects
    # the static libraries whenever they exist.
    find_package(
        Geant4 11.2.2 CONFIG REQUIRED
        COMPONENTS gdml
        OPTIONAL_COMPONENTS static)
endif ()

message(STATUS "Using Geant4 ${Geant4_VERSION} from ${Geant4_DIR}")
message(STATUS "Using Python ${Python_VERSION} from ${Python_EXECUTABLE}")

include(FetchContent)

FetchContent_Declare(
    awkward-headers
    URL https://github.com/scikit-hep/awkward/releases/download/${AWKWARD_VERSION}/header-only.zip
)
FetchContent_GetProperties(awkward-headers)
if (NOT awkward-headers_POPULATED)
    FetchContent_Populate(awkward-headers)
    add_subdirectory(${awkward-headers_SOURCE_DIR}
                     ${awkward-headers_BINARY_DIR} EXCLUDE_FROM_ALL)
endif ()

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG ${PYBIND11_VERSION}
    DOWNLOAD_EXTRACT_TIMESTAMP 1)
FetchContent_GetProperties(pybind11)
if (NOT pybind11_POPULATED)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR}
                     EXCLUDE_FROM_ALL)
endif ()

# Geant4 libraries that link Qt directly, or reach it through each other (the
# visualization drivers, UI sessions and vis manager). The physics module must
# not link any of them, so that importing the package never loads Qt.
set(GEANT4_QT_LIBRARIES
    G4OpenGL G4ToolsSG G4interfaces G4visQt3D G4vis_management G4FR G4GMocren
    G4RayTracer G4Tree G4VRML G4visHepRep G4OpenInventor G4visVtk)
set(GEANT4_PHYSICS_LIBRARIES ${Geant4_LIBRARIES})
foreach (lib IN LISTS GEANT4_QT_LIBRARIES)
    list(REMOVE_ITEM GEANT4_PHYSICS_LIBRARIES Geant4::${lib} Geant4::${lib}-static)
endforeach ()

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/geant4_application/src/*.cpp")

file(GLOB_RECURSE PYTHON_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/python/*.cpp")

get_filename_component(GEANT4_PREFIX "${Geant4_DIR}/../../.." ABSOLUTE)

pybind11_add_module(${PYTHON_MODULE_NAME} MODULE ${SOURCES} ${PYTHON_SOURCES})

target_compile_definitions(
    ${PYTHON_MODULE_NAME}
    PRIVATE VERSION_INFO=${PROJECT_VERSION}
            SKBUILD_PROJECT_VERSION=${SKBUILD_PROJECT_VERSION}
            GEANT4_VERSION=${Geant4_VERSION}
            AWKWARD_VERSION=${AWKWARD_VERSION}
            PYBIND11_VERSION=${PYBIND11_VERSION})

target_include_directories(
    ${PYTHON_MODULE_NAME}
    PRIVATE ${PROJECT_SOURCE_DIR}/src/geant4_application/include
            ${Geant4_INCLUDE_DIRS})

target_link_libraries(
    ${PYTHON_MODULE_NAME} PRIVATE ${GEANT4_PHYSICS_LIBRARIES}
                                  awkward::layout-builder pybind11::headers)

set(EXTENSION_MODULES ${PYTHON_MODULE_NAME})

if (GEANT4_PYTHON_APPLICATION_VISUALIZATION)
    pybind11_add_module(${VIS_MODULE_NAME} MODULE
                        "${PROJECT_SOURCE_DIR}/src/vis/module.cpp")
    # Leave out Geant4's Qt3D driver: the PyQt5-Qt5 wheel that provides Qt to
    # published wheels ships no Qt3D modules. Not linking Geant4::G4visQt3D also
    # drops its G4VIS_USE_QT3D define, so G4VisExecutive never references it.
    # The OpenGL Qt viewer (/vis/open OGL) is unaffected.
    set(GEANT4_VIS_LIBRARIES ${Geant4_LIBRARIES})
    list(REMOVE_ITEM GEANT4_VIS_LIBRARIES Geant4::G4visQt3D)
    target_include_directories(${VIS_MODULE_NAME} PRIVATE ${Geant4_INCLUDE_DIRS})
    target_link_libraries(${VIS_MODULE_NAME} PRIVATE ${GEANT4_VIS_LIBRARIES}
                                                     pybind11::headers)
    # Homebrew may expose Qt 6 from its global include directory while this
    # Geant4 installation was built with Qt 5. Put Qt 5's forwarding headers
    # first so framework headers do not accidentally include their Qt 6 peers.
    if (APPLE AND DEFINED Qt5Core_DIR)
        get_filename_component(QT5_PREFIX "${Qt5Core_DIR}/../../.." ABSOLUTE)
        target_include_directories(${VIS_MODULE_NAME} SYSTEM BEFORE PRIVATE
                                   "${QT5_PREFIX}/include")
    endif ()
    list(APPEND EXTENSION_MODULES ${VIS_MODULE_NAME})
endif ()

# Wheel repair tools (delocate/auditwheel) replace these with the bundled
# library locations; source installs keep finding Geant4 where it was built.
# Qt frameworks linked by @rpath (as when building against PyQt5-Qt5's Qt)
# also need their directory listed for delocate to resolve them.
set(EXTENSION_RPATH "${GEANT4_PREFIX}/lib")
if (APPLE AND DEFINED QT5_PREFIX)
    list(APPEND EXTENSION_RPATH "${QT5_PREFIX}/lib")
endif ()

foreach (module IN LISTS EXTENSION_MODULES)
    pybind11_extension(${module})
    if (NOT MSVC AND NOT ${CMAKE_BUILD_TYPE} MATCHES Debug|RelWithDebInfo)
        # Strip unnecessary sections of the binary on Linux/macOS
        pybind11_strip(${module})
    endif ()
    set_target_properties(
        ${module}
        PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${PROJECT_NAME}
                   CXX_VISIBILITY_PRESET "hidden"
                   CUDA_VISIBILITY_PRESET "hidden"
                   BUILD_RPATH "${EXTENSION_RPATH}"
                   INSTALL_RPATH "${EXTENSION_RPATH}")
endforeach ()

install(
    TARGETS ${EXTENSION_MODULES}
    LIBRARY DESTINATION ${PROJECT_NAME}
    RUNTIME DESTINATION ${PROJECT_NAME}
    ARCHIVE DESTINATION ${PROJECT_NAME})
