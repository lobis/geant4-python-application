cmake_minimum_required(VERSION 3.22)

project(Geant4PythonicApplication)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(FetchContent)

set(AWKWARD_VERSION "v2.5.0")
set(PYBIND11_VERSION "v2.11.1")

find_package(Geant4 REQUIRED CONFIG COMPONENTS gdml)

FetchContent_Declare(
    awkward-headers
    URL https://github.com/scikit-hep/awkward/releases/download/${AWKWARD_VERSION}/header-only.zip
        DOWNLOAD_EXTRACT_TIMESTAMP
        1)
# Instead of using `FetchContent_MakeAvailable(awkward-headers)`, we manually
# load the target so that we can EXCLUDE_FROM_ALL
FetchContent_GetProperties(awkward-headers)
if (NOT awkward-headers_POPULATED)
    FetchContent_Populate(awkward-headers)
    add_subdirectory(${awkward-headers_SOURCE_DIR}
                     ${awkward-headers_BINARY_DIR} EXCLUDE_FROM_ALL)
endif ()

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

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

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/geant4/*.cpp")

add_library(${PROJECT_NAME} SHARED ${SOURCES})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

target_include_directories(
    ${PROJECT_NAME}
    PUBLIC ${PROJECT_SOURCE_DIR}/include
    PRIVATE ${Geant4_INCLUDE_DIRS} ${Python3_INCLUDE_DIRS}
            ${PyBind11_INCLUDE_DIRS})

target_link_libraries(
    ${PROJECT_NAME} PUBLIC ${Geant4_LIBRARIES} awkward::layout-builder
                           pybind11::embed)

# add the pybind11 module
set(PYTHON_MODULE_NAME geant4_cpp)
file(GLOB_RECURSE PYTHON_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/python/*.cpp")
pybind11_add_module(${PYTHON_MODULE_NAME} ${PYTHON_SOURCES})
target_link_libraries(${PYTHON_MODULE_NAME} PUBLIC ${PROJECT_NAME})

if (CMAKE_BUILD_TYPE MATCHES Debug)
    message(STATUS "Building tests")
    add_subdirectory(tests)
endif ()
