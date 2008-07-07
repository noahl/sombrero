#!/usr/bin/python

# this uses python's distutils. documentation was at
# http://docs.python.org/dist/dist.html when I looked

from distutils.core import setup, Extension
import distutils.ccompiler

# First build the python extension modules

tracemodule = Extension("Trace",
                        define_macros = [("FILEVERSION", "\"2.04\"")],
                        sources = ["tracer/hat-c.c", "tracer/hat-c.i"],
                        swig_opts = ["-importall", "-I/usr/include", "-I.", "-D__x86_64__"])
                           # distutils handles SWIG!
                           # (could also add "-modern" to swig_opts)

# debugmodule: not used right now, but would presumably still compile a working tracer
debugmodule = Extension("Trace_Debug",
                        define_macros = [("FILEVERSION", "\"2.04\""), ("DEBUG", "")],
                        sources = ["hat-c.c", "hat-c.i"],
                        swig_opts = ["-importall", "-I/usr/include", "-D__x86_64__"])

# (mis?)using setup
setup (name = "Trace",
       version = "First Build",
       description = "This is a package to write Hat traces with Python",
       ext_modules = [tracemodule])

# Then build some extra executables that aren't Python extensions

cc = distutils.ccompiler.new_compiler()

temp_dir = "build" # should be a command-line option

cc.add_include_dir(".")
cc.define_macro("FILEVERSION","\"2.04\"")

# compile: this also depends on ./{art.h,ntohl.h}, but so does everything else.
# wait to list it here until there's a universal solution.
cc.compile(["hat-tools/hat-check.c"], output_dir=temp_dir, depends=["hat-tools/hat-check.c"])
cc.link_executable([temp_dir+"/hat-tools/hat-check.o"], output_progname = "hat-check"
                   output_dir=temp_dir+"/hat-tools")

