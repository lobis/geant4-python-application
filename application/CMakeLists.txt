cmake_minimum_required(VERSION 3.10)

project(libGeant4PythonicApplication)

set(CMAKE_CXX_STANDARD 17)

find_package(Geant4 REQUIRED)

include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG v2.11.1)
FetchContent_MakeAvailable(pybind11)

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "${PROJECT_SOURCE_DIR}/src/*.cpp")

add_library(${PROJECT_NAME} SHARED ${SOURCES})

target_include_directories(
    ${PROJECT_NAME}
    PUBLIC ${PROJECT_SOURCE_DIR}/include
    PRIVATE ${Geant4_INCLUDE_DIRS})

target_link_libraries(${PROJECT_NAME} PUBLIC ${Geant4_LIBRARIES})

if (CMAKE_BUILD_TYPE MATCHES Debug)
    message(STATUS "Debug build, adding tests")
    add_subdirectory(tests)
endif ()
