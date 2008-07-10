/* This uses SWIG, the Simplified Wrapper and Interface Generator, to
 * generate a Python interface for the hat-c code. documentation was at
 * http://www.swig.org/doc.html when I looked */

%module Artutils

%{
#include "artutils.h"
%}

%include "artutils.h"
%include "typemaps.i" /* for INPUT and OUTPUT parameters */

int freadAt(FileOffset fo, void *OUTPUT, int size, int nmemb, FILE *stream);
int q_fread(void *OUTPUT, int size, int nmemb, FILE *stream);
void readModuleAt(FileOffset fo, char **OUTPUT, char **OUTPUT, Bool *OUTPUT);
FileOffset readTraceAt(FileOffset fo, char **OUTPUT, SrcRef **OUTPUT,
                       int *OUTPUT, int *followHidden, int depth);
