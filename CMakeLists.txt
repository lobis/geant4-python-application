cmake_minimum_required(VERSION 3.25...3.30)

set(CMAKE_CXX_STANDARD 17)

set(AWKWARD_VERSION "v2.6.9")
set(PYBIND11_VERSION "v2.13.6")
set(Geant4_VERSION "11.2.2")

if (NOT DEFINED SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME geant4-python-application) # required for JetBrains IDEs to show a readable name
endif ()

project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYTHON_MODULE_NAME _geant4_application)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(
    Python
    COMPONENTS Interpreter Development.Module
    REQUIRED)

set(GEANT4_COMPONENTS "gdml")
if (CMAKE_BUILD_TYPE STREQUAL "Release")
    set(GEANT4_COMPONENTS "gdml static")
endif ()

find_package(
    Geant4 ${Geant4_VERSION} CONFIG
    COMPONENTS ${GEANT4_COMPONENTS}
    REQUIRED)

message(STATUS "Using CMake ${CMAKE_VERSION}. CMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}")
message(STATUS "Using Python ${Python_VERSION} from ${Python_EXECUTABLE}")
message(STATUS "Using awkward ${AWKWARD_VERSION}")
message(STATUS "Using pybind11 ${PYBIND11_VERSION}")
message(STATUS "Using Geant4 ${Geant4_VERSION} from ${Geant4_DIR} with components: ${GEANT4_COMPONENTS}")

include(FetchContent)

FetchContent_Declare(
    awkward-headers
    URL https://github.com/scikit-hep/awkward/releases/download/${AWKWARD_VERSION}/header-only.zip
)
FetchContent_GetProperties(awkward-headers)
if (NOT awkward-headers_POPULATED)
    FetchContent_MakeAvailable(awkward-headers)
endif ()

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG ${PYBIND11_VERSION}
    DOWNLOAD_EXTRACT_TIMESTAMP 1)
FetchContent_GetProperties(pybind11)
if (NOT pybind11_POPULATED)
    FetchContent_MakeAvailable(pybind11)
endif ()

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/geant4_application/src/*.cpp")

file(GLOB_RECURSE PYTHON_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/python/*.cpp")

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
    ${PYTHON_MODULE_NAME} PRIVATE ${Geant4_LIBRARIES} awkward::layout-builder
                                  pybind11::headers)

pybind11_extension(${PYTHON_MODULE_NAME})
if (NOT MSVC AND NOT ${CMAKE_BUILD_TYPE} MATCHES Debug|RelWithDebInfo)
    # Strip unnecessary sections of the binary on Linux/macOS
    pybind11_strip(${PYTHON_MODULE_NAME})
endif ()

set_target_properties(
    ${PYTHON_MODULE_NAME}
    PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${PROJECT_NAME}
               CXX_VISIBILITY_PRESET "hidden"
               CUDA_VISIBILITY_PRESET "hidden")

install(
    TARGETS ${PYTHON_MODULE_NAME}
    LIBRARY DESTINATION ${PROJECT_NAME}
    RUNTIME DESTINATION ${PROJECT_NAME}
    ARCHIVE DESTINATION ${PROJECT_NAME})
