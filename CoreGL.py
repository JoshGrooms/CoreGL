#!/usr/bin/python3.5

# CHANGELOG
# Written by Josh Grooms on 20151023
#   20160705 - Updated this script for cross-platform usage (i.e. on Windows & Linux) and to utilize Python 3.5 instead of
#              Python 2 functions.

import argparse
import os
import platform
import re
import sys
import urllib.request



## DOCUMENTATION ##
def Help():
    return """
    COREGL - A simple Python script that loads a pure OpenGL Core API profile for use in C or C++ programs.

        Running this script will generate two new files called 'OpenGL.c' and 'OpenGL.h' that can be imported into any C or
        C++ program being developed by the user. Doing so affords easy access to functions from the OpenGL Core Profile
        without having to manually write the code that loads OpenGL function pointers (e.g. using 'glXGetProcAddress' on
        Linux or 'wglGetProcAddress' on Windows).

    SYNTAX:
        CoreGL
        CoreGL options

    OPTIONS:
        --destination:  The path to which all newly generated files will be written. This is where the 'OpenGL.c' and
                        'OpenGL.h' files that can be used in C/C++ projects can be found.
                        DEFAULT: ./Generated

        -h, --help:     Display the documentation for this script (i.e. what you're currently reading) in the console window.

        --platform:     The name of the operating system or platform on which OpenGL development will occur. This option
                        controls the versions of the templates used to generate the C/C++ function loading code. By default,
                        this script chooses templates by querying the underlying platform name at runtime, but this behavior
                        can be overridden through this argument.
                        DEFAULT: platform.system()
                        OPTIONS:
                            Linux
                            Windows

        --source:       The full or relative path to an OpenGL Core Profile header.
                        DEFAULT: /usr/include/GL/glcorearb.h
    """



## SCRIPT VARIABLES ##
# Private
AppDir              = os.path.dirname(os.path.realpath(__file__))
TemplateDir         = AppDir + os.path.sep + 'Templates'
HeaderTemplateName  = 'OpenGL.h'
SourceTemplateName  = 'OpenGL.c'

# Publically modifiable (via input arguments)
InstallDestination  = AppDir + os.path.sep + 'Generated'
OpenGLHeaderPath    = '/usr/include/GL/glcorearb.h'
OpenGLHeaderURL     = 'https://www.opengl.org/registry/api/GL/glcorearb.h'
PlatformName        = platform.system()



## PRIVATE UTILITY FUNCTIONS
def AssertHeaderExistence(glHeaderPath):
    if not os.path.exists(glHeaderPath):
        print("ERROR: Could not find the OpenGL API header file {0}. Ensure that this file exists at the specified path before running this program.", glHeaderPath)
        sys.exit(0)

def CreateHeaderDeclaration(funName, space):
    '''
    CREATEHEADERDECLARATION - Creates an OpenGL API function declaration string in the header that this program generates.

    OUTPUT:
        d:          STRING
                    A string of text representing a variable declaration that will be used to store an OpenGL function
                    pointer. This declaration is meant to be placed in the C header file that this program generates (not in
                    the source file), and as such it is decorated with an "extern" keyword.
    INPUT:
        funName:    STRING
                    The name of the OpenGL function being declared.

        space:      INT
                    The number of individual spaces between the type and the variable name for this declaration. This is used
                    to neatly align the generated text in order to improve readability.
    '''
    return '\t\t\textern PFN{0}PROC{1}{2};'.format(funName.upper(), ' ' * space, '_cglptr_' + funName)

def CreateHeaderMacro(funName, space):
    '''
    CREATEHEADERMACRO - Creates a macro definition string in the header file that this program generates.

        This function creates macro definitions that alias the internally used OpenGL function pointer names. This allows C
        or C++ programs using the generated files to call API functions as if they possessed their originally defined names
        (e.g. 'glCreateTextures' instead of '_cglptr_glCreateTextures').

        Without these, we would be forced to call function pointers whose names are prepended with a '_cglptr_' decoration
        (or something else unique) because some OpenGL functions are loaded independently by other commonly used libraries.
        If this were to occur and we tried to re-define those function pointers within the files generated here, segmentation
        faults would be observed at runtime.

    OUTPUT:
        m:          STRING
                    A string of text representing the definition of a macro that allows for easily calling OpenGL API
                    functions using the generated files. This definition is meant to be placed in the C header file that this
                    program generates (not in the source file).

    INPUTS:
        funName:    STRING
                    The name of the OpenGL function being declared.

        space:      INT
                    The number of individual spaces between the macro name and the function pointer to which it refers. This
                    is used to neatly align the generated text in order to improve readability.
    '''
    return '\t\t\t#define {0}{1}{2}'.format(funName, ' ' * (space + 6), '_cglptr_' + funName)

def CreateLoadingCode(glHeaderContent):
    '''
    CREATELOADINGCODE - Creates the C-language code strings that are placed into the generated source and header files.

        This function creates the source code that will appear inside of the new files produced by this program. These code
        strings contain the instructions that ultimately load the OpenGL library for some C or C++ program.

    OUTPUTS:
        hdrDeclarations:    STRING

        hdrMacros:          STRING

        srcDeclarations:    STRING

        srcValues:          STRING

    INPUT:
        glHeaderContent:    STRING[]
                            The entire content of a 'glcorearb.h' (or other OpenGL header) file as a single string. This
                            string may be obtained from either a downloaded file (from the OpenGL website) or from a file
                            that resides on the computer.
    '''

    funSignatures = []

    maxFunNameLength = 0
    rxp = re.compile(r'^GLAPI(.*)APIENTRY\s+(\w+)\s*(\(.*\));$')
    for line in glHeaderContent.splitlines():
        m = rxp.match(str(line))
        if m:
            outArg = m.group(1)
            funName = m.group(2)
            inArgs = m.group(3)

            maxFunNameLength = max(maxFunNameLength, len(funName))
            funSignatures.append((outArg, funName, inArgs))

    rightAlign = maxFunNameLength + 4
    funSignatures.sort(key = lambda x: x[1])

    hdrDeclarations = []
    hdrMacros = []
    srcDeclarations = []
    srcValues = []

    for sig in funSignatures:
        name = sig[1]
        space = rightAlign - len(name)
        hdrDeclarations.append(CreateHeaderDeclaration(name, space))
        hdrMacros.append(CreateHeaderMacro(name, space))
        srcDeclarations.append(CreateSourceDeclaration(name, space))
        srcValues.append(CreateSourceValue(name, space))

    hdrDeclarations = '\n'.join(hdrDeclarations)
    hdrMacros = '\n'.join(hdrMacros)
    srcDeclarations = '\n'.join(srcDeclarations)
    srcValues = '\n'.join(srcValues)

    return (hdrDeclarations, hdrMacros, srcDeclarations, srcValues)

def CreateSourceDeclaration(funName, space):
    '''
    CREATESOURCEDECLARATION - Creates an OpenGL function pointer declaration in the source file that this program generates.

    SYNTAX:
        d = CreateSourceDeclaration(funName, space)

    OUTPUT:
        d:          STRING
                    A string of text representing a variable declaration that will be used to store an OpenGL function
                    pointer. This declaration is meant to be placed in the C source code file that this program generates
                    (not in the header file).

    INPUTS:
        funName:    STRING
                    The ordinary, human-readable name of an OpenGL function, with camel-casing exactly as found in the
                    official API header files. For example: 'glCreateTextures'.

        space:      INT
                    The number of individual spaces between the type and the variable name for this declaration. This is used
                    to neatly align the generated text in order to improve readability.
    '''
    return 'PFN{0}PROC{1}{2} = NULL;'.format(funName.upper(), ' ' * space, '_cglptr_' + funName)

def CreateSourceValue(funName, space):
    '''
    CREATESOURCEVALUE - Creates a line of code that fills in the values for OpenGL API function pointer declarations.
    '''
    return '\t{0}{1}= (PFN{2}PROC)glGetFunctionPointer("{3}");'.format('_cglptr_' + funName, ' ' * space, funName.upper(), funName)

def Execute(opts):
    '''
    EXECUTE - Creates the code files that load OpenGL API functions for a C or C++ program at runtime.

    INPUT:
        opts:   argparse.Namespace
                A data structure (which is actually an esoteric custom-written object called 'Namespace', because Python is
                ridiculous) that contains input arguments for this program delivered via command line. See the main function
                of this script for possible field names.
    '''

    if not os.path.exists(opts.InstallDestination):
        os.makedirs(opts.InstallDestination)

    if os.path.exists(opts.OpenGLHeaderPath):
        print("Found glcorearb.h at: {0}".format(opts.OpenGLHeaderPath))
        glAPI = ReadFile(opts.OpenGLHeaderPath + os.path.sep + "glcorearb.h")
    else:
        print("Could not locate a local copy of the OpenGL Core Profile header at: {0}".format(opts.OpenGLHeaderPath))
        print("Downloading a copy of the header file from: {0}".format(opts.OpenGLHeaderURL))
        glAPI = ReadURL(OpenGLHeaderURL)
        WriteFile(InstallDestination + os.path.sep + 'glcorearb.h', glAPI)
        print("glcorearb.h header file can be found at: {0}".format(opts.InstallDestination))

    hdrCode = ReadFile(TemplateDir + os.path.sep + HeaderTemplateName + '.' + PlatformName.lower())
    srcCode = ReadFile(TemplateDir + os.path.sep + SourceTemplateName + '.' + PlatformName.lower())

    hdrDecl, hdrMacro, srcDecl, srcVal = CreateLoadingCode(glAPI)

    hdrCode = hdrCode.format(HeaderFunctionDeclarations = hdrDecl, HeaderMacroDefinitions = hdrMacro)
    srcCode = srcCode.format(SourceFunctionDeclarations = srcDecl, SourceFunctionValues = srcVal)

    dstHeader = opts.InstallDestination + os.path.sep + HeaderTemplateName
    dstSource = opts.InstallDestination + os.path.sep + SourceTemplateName

    WriteFile(dstHeader, hdrCode)
    WriteFile(dstSource, srcCode)

    print("The OpenGL library loading files were written to: {0}".format(opts.InstallDestination))


def ReadFile(filePath):
    '''
    READFILE - Reads the file located at the path string 'filePath' and returns its contents as a single string.
    '''
    with open(filePath) as file:
        text = file.read()
    return text

def ReadURL(url):
    '''
    READURL - Reads the contents of an Internet website at the string 'url' and returns them as a single string.
    '''
    with urllib.request.urlopen(url) as response:
        text = response.read().decode('utf-8')
    return text

def WriteFile(filePath, text):
    '''
    WRITEFILE - Write a string of text to the specified file.

        This function writes text to the file at the inputted path string. If the file in question already exists, then its
        contents are completely overwritten upon executing this code. However, if this file does not exist, then it is
        automatically created before filling it with the text.

    INPUT:
        filePath:   STRING
                    A full or relative path string to the file to which text will be written. If this file already exists,
                    its contents will be overwritten. Otherwise, a new file will be created and populated with text.

        text:       STRING
                    A string of text that will be written to the designated file.
    '''
    with open(filePath, 'wb') as file:
        file.write(bytes(text, 'utf-8'))



## PROGRAM ENTRY POINT ##
if __name__ == "__main__":

    optParser = argparse.ArgumentParser(usage = Help(), add_help = False);
    optParser.add_argument('-h', action = 'store_true', dest = 'DisplayHelp')
    optParser.add_argument('--help', action = 'store_true', dest = 'DisplayHelp')
    optParser.add_argument('--destination', action = 'store', dest = 'InstallDestination')
    optParser.add_argument('--platform', action = 'store', dest = 'PlatformName')
    optParser.add_argument('--source', action = 'store', dest = 'OpenGLHeaderPath')
    optParser.add_argument('--url', action = 'store', dest = 'OpenGLHeaderURL')
    opts = optParser.parse_args()

    if opts.DisplayHelp:
        print(Help())
        sys.exit(0)

    if not opts.InstallDestination:
        opts.InstallDestination = InstallDestination
    if not opts.OpenGLHeaderPath:
        opts.OpenGLHeaderPath = OpenGLHeaderPath
    if not opts.OpenGLHeaderURL:
        opts.OpenGLHeaderURL = OpenGLHeaderURL
    if not opts.PlatformName:
        opts.PlatformName = PlatformName

    Execute(opts)
