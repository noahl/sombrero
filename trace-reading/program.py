#!/usr/bin/python

import Artutils

# the Program class represents a traced program
# this implementation returns information from a Hat trace file

class Program(object):
	def __init__(self, fileoffset):
		# at least we can do a little type checking
		if isinstance(fileoffset, int): # int should be FileOffset here
			self.fo = fileoffset
		else:
			raise Exception("Program created with invalid offset \
			                 type %s" % str(fileoffset.__class__))
	
	def parent(self):
		# return a program object
	
	def children(self):
		# return a list of program objects
	
	def result(self):
		# return a program object
	
	def name(self):
		# return a string


def makeProgramFromString(string, state):
	Make a program object from the string in the given state

