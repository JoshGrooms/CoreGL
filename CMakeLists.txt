cmake_minimum_required(VERSION 3.11)
project(TestCoreGL)
find_package(GLUT REQUIRED)
find_package(OpenGL REQUIRED)

set(CMAKE_CXX_STANDARD 17)
add_executable(TestCoreGL TestCoreGL.c)
add_library(LibCoreGL SHARED GL/OpenGL.c)

target_include_directories(
    LibCoreGL
    PUBLIC ${PROJECT_SOURCE_DIR}
)
target_link_libraries(
    LibCoreGL

    GL
    glut
    dl
)
target_include_directories(
    TestCoreGL
    PUBLIC ${PROJECT_SOURCE_DIR}
)
target_link_libraries(
    TestCoreGL

    LibCoreGL
)
