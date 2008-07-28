#!/usr/bin/python

# this uses python's distutils. documentation was at
# http://docs.python.org/dist/dist.html when I looked

from distutils.core import setup, Extension
import distutils.ccompiler
import distutils.dir_util # we need this for a terrible hack.
import os                 # and we need this for the same hack.

# First build the python extension modules

# Note on SWIG:
# Distutils "handles" SWIG. However, it doesn't do it very nicely. In order to
# build a SWIG extension, you run the swig command on the .i file. For Python
# extensions, this produces both a C file, to be compiled, and a Python file,
# to be used as-is. Unfortunately, Distutils thinks that compiling an extension
# produces only a C extension file, and I don't see any way to make it aware of
# the fact that SWIG makes two. The offical method seems to be to pretend that
# the SWIG-generated Python file was always there as part of the source, but
# this seems like a bad idea.
# However, in order to make this work, I'm essentially doing just that. The
# extension modules here all have names beginning with an underscore. The
# modules that you will want to use will *not* have names beginning with an
# underscore, but I can't tell Distutils that right now.

tracemodule = Extension("_Trace",
                        define_macros = [("FILEVERSION", "\"2.04\"")],
                        sources = ["tracer/hat-c.c", "tracer/hat-c.i"],
                        swig_opts = ["-importall", "-I/usr/include", "-I."],
                        include_dirs = ["."])
                           # distutils handles SWIG!
                           # (could also add "-modern" to swig_opts)
      # NOTE: if you're building this on an x86-64 computer, you might need to
      #       add another SWIG option: "-D__x86_64__"

# debugmodule: not used right now, but would presumably still compile a working tracer
debugmodule = Extension("_Trace_Debug",
                        define_macros = [("FILEVERSION", "\"2.04\""), ("DEBUG", "")],
                        sources = ["hat-c.c", "hat-c.i"],
                        swig_opts = ["-importall", "-I/usr/include", "-I."],
                        include_dirs = ["."])

artutilsmodule = Extension("_Artutils",
                           define_macros = [("FILEVERSION", "\"2.04\""),
                                            ("VERSION", "\"2.05\"")],
                           sources = ["trace-reading/artutils.c",
                                      "trace-reading/pathutils.c",
                                      "trace-reading/detectutils.c",
                                      "trace-reading/artutils.i"],
                           swig_opts = ["-importall", "-I/usr/include", "-I."],
                           include_dirs = ["."])

artmodule = Extension("_Art",
                      sources = ["trace-reading/art.i"],
                      swig_opts = ["-importall", "-I/usr/include", "-I."],
                      include_dirs = ["."])

# (mis?)using setup
setup (name = "Trace",
       version = "First Build",
       description = "This is a package to write Hat traces with Python",
       ext_modules = [tracemodule, artutilsmodule, artmodule])

# XXX - HACK!
for l in os.listdir("build"): # for everything in the "build" directory
	if l.startswith("lib"): # if it starts with "lib"
		# copy it to our own 'lib' directory
		distutils.dir_util.copy_tree("build/"+l, "lib")

# Then build some extra executables that aren't Python extensions

cc = distutils.ccompiler.new_compiler()

temp_dir = "build" # should be a command-line option

cc.add_include_dir(".")
cc.define_macro("FILEVERSION","\"2.04\"")

# compile: this also depends on ./{art.h,ntohl.h}, but so does everything else.
# wait to list it here until there's a universal solution.
cc.compile(["hat-tools/hat-check.c"], output_dir=temp_dir, depends=["hat-tools/hat-check.c"])
cc.link_executable([temp_dir+"/hat-tools/hat-check.o"], output_progname = "hat-check",
                   output_dir=temp_dir+"/hat-tools")

