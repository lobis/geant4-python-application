cmake_minimum_required(VERSION 3.25...3.28)

if (NOT DEFINED SKBUILD_PROJECT_NAME)
    # IDE
    set(SKBUILD_PROJECT_NAME geant4-python-application)
endif ()

if (NOT DEFINED SKBUILD_PROJECT_VERSION)
    # IDE
    set(SKBUILD_PROJECT_VERSION 0.0.0.ide)
endif ()

string(REGEX MATCHALL "[^.]+" SKBUILD_PROJECT_VERSION_COMPONENTS
             "${SKBUILD_PROJECT_VERSION}")
list(GET SKBUILD_PROJECT_VERSION_COMPONENTS 0 SKBUILD_PROJECT_VERSION_MAJOR)
list(GET SKBUILD_PROJECT_VERSION_COMPONENTS 1 SKBUILD_PROJECT_VERSION_MINOR)
list(GET SKBUILD_PROJECT_VERSION_COMPONENTS 2 SKBUILD_PROJECT_VERSION_PATCH)
list(LENGTH SKBUILD_PROJECT_VERSION_COMPONENTS version_components_length)
if (version_components_length GREATER 3)
    list(GET SKBUILD_PROJECT_VERSION_COMPONENTS 3
         SKBUILD_PROJECT_VERSION_SUFFIX)
else ()
    set(SKBUILD_PROJECT_VERSION_SUFFIX "")
endif ()

# join version components (cannot put suffix in 'project')
string(
    CONCAT SKBUILD_PROJECT_VERSION_NO_SUFFIX ${SKBUILD_PROJECT_VERSION_MAJOR}
           "." ${SKBUILD_PROJECT_VERSION_MINOR} "."
           ${SKBUILD_PROJECT_VERSION_PATCH})

project(
    ${SKBUILD_PROJECT_NAME}
    LANGUAGES CXX
    VERSION ${SKBUILD_PROJECT_VERSION_NO_SUFFIX})

if (MSVC)
    if (CMAKE_CXX_FLAGS MATCHES "/W[0-4]")
        string(REGEX REPLACE "/W[0-4]" "/W3" CMAKE_CXX_FLAGS
                             "${CMAKE_CXX_FLAGS}")
    else ()
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W3")
    endif ()
elseif (CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wno-long-long")
endif ()

set(PYTHON_MODULE_NAME _geant4_application)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(AWKWARD_VERSION "v2.5.0")
set(PYBIND11_VERSION "v2.11.1")

find_package(
    Python
    COMPONENTS Interpreter Development.Module
    REQUIRED)
find_package(
    Geant4 11.2.0 CONFIG
    COMPONENTS gdml static
    REQUIRED)

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
