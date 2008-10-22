#!/usr/bin/python

import types # for BuiltinsMap

# this file handles the Python environments for the tracing interpreter.

_frames = [BuiltinsMap()]

# BuiltinsMap: act like a dictionary that holds the builtin functions,
#              but write their traces lazily.
class BuiltinsMap(object):
	def __getitem__(self, name):
		try:
			val, atom = self.prims[name]
