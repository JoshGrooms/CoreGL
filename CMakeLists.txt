cmake_minimum_required(VERSION 3.0)
project(CoreGL)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c11")

add_executable(CoreGL TestCoreGL.c)

add_library(LibCoreGL SHARED Generated/OpenGL.c)

target_link_libraries(LibCoreGL
    GL
    glut
    dl
)

target_link_libraries(CoreGL LibCoreGL)
