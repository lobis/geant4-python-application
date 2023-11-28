include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
        DOWNLOAD_EXTRACT_TIMESTAMP
        1)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt
    ON
    CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

set(TEST_EXECUTABLE_NAME ${PROJECT_NAME}Test)

file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS
     "${PROJECT_SOURCE_DIR}/tests/*.cpp")
add_executable(${TEST_EXECUTABLE_NAME})
target_sources(${TEST_EXECUTABLE_NAME} PRIVATE ${TEST_SOURCES})
target_include_directories(${TEST_EXECUTABLE_NAME}
                           PRIVATE ${PROJECT_SOURCE_DIR}/include)
target_link_libraries(${TEST_EXECUTABLE_NAME} ${PROJECT_NAME} GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(${TEST_EXECUTABLE_NAME})
