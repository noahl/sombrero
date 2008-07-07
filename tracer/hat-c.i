/* This uses SWIG, the Simplified Wrapper and Interface Generator, to
 * generate a Python interface for the hat-c code. documentation was at
 * http://www.swig.org/doc.html when I looked */

%module Trace

%{
#include "hat-c.h"
%}

/* This file now works. However, SWIG doesn't know what a FileOffset is, and
 * therefore wraps it with a pointer. I could make this much faster by giving
 * SWIG the typedef for FileOffset (it's a uint32_t). */

%include "hat-c.h"

