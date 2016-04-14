# Automatically Load the OpenGL Core Profile Functions

## About
PurityGL is a package in exactly the same vein as [GL3W](https://github.com/skaslev/gl3w) (from which it drew heavy inspiration) and other similar offerings. It provides a way to automatically load the latest OpenGL core profile functions for use within a C/C++ program. However, unlike GL3W, PurityGL does not download anything from the Internet or reach out to the world in any way. Instead, it uses the 'glcorearb.h' file already present on your system to generate the needed files, avoiding any need to update hyperlinks as they break and using pre-installed files that are comparatively well-known.



## Requirements
- An existing 'glcorearb.h' header file on your Linux system.
    - Typically, this is found in the directory: /usr/include/GL

- GLUT (only when running the testing program).



## Instructions
1. Download this repository into any folder that you want (probably a coding project somewhere).

2. Run the code generation Python script 'PurityGL.py' via the command line:
    - python ./PurityGL.py

3. In the newly created 'Generated' directory, you'll find a C source and header file that can be used immediately with your C/C++ application. These generated files may be tested via the included C program 'TestPurityGL.c'.
    - Compile the testing program with the included Bash script named 'build', then run the outputted executable. If a blank window shows up, the OpenGL core profile was successfully loaded.

4. Within your OpenGL-enabled C/C++ program, invoke 'glLoadFunctions()' wherever you please to load the OpenGL function pointers at runtime.
