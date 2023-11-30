cmake_minimum_required(VERSION 3.25)

project(Geant4PythonicApplication)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Geant4 REQUIRED CONFIG COMPONENTS gdml)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

add_subdirectory(external/awkward/header-only)
add_subdirectory(external/pybind11)

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/geant4/*.cpp")

add_library(${PROJECT_NAME} STATIC ${SOURCES})

target_compile_options(${PROJECT_NAME} PUBLIC -fPIC)
set_target_properties(
    ${PROJECT_NAME}
    PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib
               ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib)

target_include_directories(${PROJECT_NAME} PUBLIC ${PROJECT_SOURCE_DIR}/include
                                                  ${Geant4_INCLUDE_DIRS})

target_link_libraries(
    ${PROJECT_NAME}
    PUBLIC ${Geant4_LIBRARIES} awkward::layout-builder pybind11::embed
           pybind11::module ${Python3_LIBRARY} Python3::Module)

set(PYTHON_MODULE_NAME geant4_cpp)
file(GLOB_RECURSE PYTHON_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/src/python/*.cpp")
pybind11_add_module(${PYTHON_MODULE_NAME} ${PYTHON_SOURCES})
target_link_libraries(${PYTHON_MODULE_NAME} PRIVATE ${PROJECT_NAME})
target_compile_options(${PYTHON_MODULE_NAME} PRIVATE -fPIC)
set_target_properties(
    ${PYTHON_MODULE_NAME}
    PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib
               ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib
               CXX_VISIBILITY_PRESET hidden
               VISIBILITY_INLINES_HIDDEN ON
               CXX_EXTENSIONS NO)

install(
    TARGETS ${PROJECT_NAME} ${PYTHON_MODULE_NAME}
    LIBRARY DESTINATION "lib"
    RUNTIME DESTINATION "lib"
    ARCHIVE DESTINATION "lib")

# -DWITH_TESTS=ON
if (WITH_TESTS)
    message(STATUS "Building tests")
    add_subdirectory(tests)
endif ()
