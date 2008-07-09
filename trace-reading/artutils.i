/* This uses SWIG, the Simplified Wrapper and Interface Generator, to
 * generate a Python interface for the hat-c code. documentation was at
 * http://www.swig.org/doc.html when I looked */

%module Artutils

%{
#include "artutils.h"
%}

%include "artutils.h"
