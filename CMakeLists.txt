cmake_minimum_required(VERSION 3.25)

project(
    ${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Geant4 REQUIRED CONFIG COMPONENTS gdml)
find_package(
    Python3
    COMPONENTS Interpreter Development.Module
    REQUIRED)

add_subdirectory(external/awkward/header-only)
add_subdirectory(external/pybind11)

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/geant4/*.cpp")

set(PYTHON_MODULE_NAME _core)
file(GLOB_RECURSE PYTHON_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/python/*.cpp")

pybind11_add_module(${PYTHON_MODULE_NAME} ${PYTHON_SOURCES})
target_compile_options(${PYTHON_MODULE_NAME} PRIVATE -fPIC)
target_compile_definitions(${PYTHON_MODULE_NAME}
                           PRIVATE VERSION_INFO=${PROJECT_VERSION})
target_include_directories(
    ${PYTHON_MODULE_NAME} PUBLIC ${PROJECT_SOURCE_DIR}/include
                                 ${Geant4_INCLUDE_DIRS})
target_sources(${PYTHON_MODULE_NAME} PRIVATE ${SOURCES})
target_link_libraries(
    ${PYTHON_MODULE_NAME}
    PRIVATE ${Geant4_LIBRARIES}
            awkward::layout-builder
            pybind11::embed
            pybind11::module
            ${Python3_LIBRARY}
            Python3::Module
            pybind11::headers)

set_target_properties(
    ${PYTHON_MODULE_NAME}
    PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib
               ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib
               CXX_VISIBILITY_PRESET hidden
               VISIBILITY_INLINES_HIDDEN ON
               CXX_EXTENSIONS NO)

install(
    TARGETS ${PYTHON_MODULE_NAME}
    LIBRARY DESTINATION ${PROJECT_NAME}
    RUNTIME DESTINATION ${PROJECT_NAME}
    ARCHIVE DESTINATION ${PROJECT_NAME})
