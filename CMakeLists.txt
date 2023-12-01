cmake_minimum_required(VERSION 3.15...3.27)

if (NOT DEFINED SKBUILD_PROJECT_NAME)
    # IDE
    set(SKBUILD_PROJECT_NAME geant4-python-application)
endif ()

project(
    ${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX)

set(PYTHON_MODULE_NAME _core)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(
    Python
    COMPONENTS Interpreter Development.Module
    REQUIRED)
find_package(Geant4 REQUIRED CONFIG COMPONENTS gdml)

message(STATUS "Using Geant4 ${Geant4_VERSION} from ${Geant4_DIR}")
message(STATUS "Using Python ${Python_VERSION} from ${Python_EXECUTABLE}")

add_subdirectory(external/awkward/header-only)
add_subdirectory(external/pybind11)

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/geant4/*.cpp")

file(GLOB_RECURSE PYTHON_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/python/*.cpp")

pybind11_add_module(${PYTHON_MODULE_NAME} MODULE ${SOURCES} ${PYTHON_SOURCES})

target_compile_definitions(
    ${PYTHON_MODULE_NAME} PRIVATE VERSION_INFO=${PROJECT_VERSION}
                                  GEANT4_VERSION=${Geant4_VERSION}
                                  )

target_include_directories(
    ${PYTHON_MODULE_NAME} PRIVATE ${PROJECT_SOURCE_DIR}/include
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
