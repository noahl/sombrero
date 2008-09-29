/* This uses SWIG, the Simplified Wrapper and Interface Generator, to
 * generate a Python interface for the hat-c code. documentation was at
 * http://www.swig.org/doc.html when I looked */

%module Trace

%{
#include "hat-c.h"

extern void hat_Open(char *progname);
%}

extern void hat_Open(char *progname);

%ignore hat_Open;

%include "hat-c.h"
