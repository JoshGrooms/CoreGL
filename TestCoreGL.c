/* CHANGELOG
 * Written by Josh Grooms on 20151025
 */

#include "GL/OpenGL.h"

#include <GL/glut.h>
#include <stdbool.h>
#include <stdio.h>



static void Present()
{
    glClearColor(0.5f, 0.5f, 0.5f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glutSwapBuffers();
    glutPostRedisplay();
}

static void Resize(int width, int height)
{
    if (width < 1)
        width = 1;
    if (height < 1)
        height = 1;

    glViewport(0, 0, width, height);
    glClearDepth(1.0f);
    glClearColor(0.5f, 0.5f, 0.5f, 1.0f);
    glEnable(GL_DEPTH_TEST);
}

int main(int nargs, char** args)
{
    glutInit(&nargs, args);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH);
    glutInitWindowPosition(100, 100);
    glutInitWindowSize(500, 500);
    glutCreateWindow("PureGL");

    glutReshapeFunc(Resize);
    glutDisplayFunc(Present);

    if (!glLoadFunctions())
    {
        fprintf(stderr, "Failed to load the OpenGL Core Profile library.\n");
        return -1;
    }

    glutMainLoop();
    return 1;
}
