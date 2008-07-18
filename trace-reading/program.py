#!/usr/bin/python

import Artutils

# the Program class represents a traced program
# this implementation returns information from a Hat trace file

# for right now, just return dummy objects to test the UI with.
class Program(object):
	def __init__(self, fileoffset):
		# at least we can do a little type checking
		if isinstance(fileoffset, int): # int should be FileOffset here
			self.fo = fileoffset
		else:
			raise Exception("Program created with invalid offset \
			                 type %s" % str(fileoffset.__class__))
	
	def parent(self):
		# return a program object or None
		return Program(3)
	
	def children(self):
		# return a (possibly empty) list of program objects
		return [Program(5), Program(6)]
	
	def result(self):
		# return a program object
		return Program(17)
	
	def name(self):
		# return a string
		return ("Program at fileoffset " + str(self.fo))


# makeProgramFromString: make a Program from the given string, with the given
#                        global state
def makeProgramFromString(string, state):
	# this function is actually not correctly implemented right now.
	# no matter what the string is, it will just return the offset of the
	# use of the function 'main' in the trace state.hatfile.
	if hasattr(state, "hatfile"):
		return Program(Artutils.findMainUse(True))
	else:
		raise Exception("You can't run a program with no file open!")

# class State: holds the state of a computer. Provides the environment for
# executing programs.
# right now, this is a completely unnecessary dummy class
class State(object):
	def import_file(self, filename):
		print "Importing file", repr(filename), "!"
		f = open(filename)
		Artutils.openHatFile("Test", filename)
		self.hatfile = filename

