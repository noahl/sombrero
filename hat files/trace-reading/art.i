/* This uses SWIG, the Simplified Wrapper and Interface Generator, to
 * generate a Python interface for the hat-c code. documentation was at
 * http://www.swig.org/doc.html when I looked */

/* We're wrapping art.h separately, instead of making it part of Artutils,
 * because I can't figure out how to make swig include it from artutils.i.
 * Eventually, it would be better to merge these two modules, unless something
 * else starts using this one too. */

%module Art

%header %{
#include "art.h"
%}

%include "art.h"
