/* This uses SWIG, the Simplified Wrapper and Interface Generator, to
 * generate a Python interface for the hat-c code. documentation was at
 * http://www.swig.org/doc.html when I looked */

%module Artutils

%header %{
#include "artutils.h"
%}

/* the functions we're ignoring here are both totally wrappable with SWIG.
 * However, I don't think we'll actually need either of them, and it doesn't
 * seem worth the effort to learn SWIG pointer handling and make them work. */
%ignore freadAt;
%ignore q_fread;

/* the next functions aren't being wrapped either, even though they might be
 * very useful, because wrapping them takes time, and I'd rather spend my time
 * on things I *know* will be useful. I'll come back and make these work if I
 * hit a point in the Python code where I want to use them. */
%ignore readModuleAt;
%ignore readTraceAt;

/* finally, these next two functions return chars that should be interpreted as
 * very small integers. we redeclare them so that SWIG will do this. */
int q_peek();
int q_tag();

%ignore q_peek;
%ignore q_tag;

%include "artutils.h"

