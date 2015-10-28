cmake_minimum_required(VERSION 3.0)
project(PurityGL)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c11")

add_executable(PurityGL TestPurityGL.c)

add_library(LibPurityGL SHARED Generated/OpenGL.c)

target_link_libraries(LibPurityGL
    GL
    glut
    dl
)

target_link_libraries(PurityGL LibPurityGL)
