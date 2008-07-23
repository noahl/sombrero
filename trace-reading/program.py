#!/usr/bin/python

import Artutils
import Art

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
		
		self.typ = Artutils.getNodeType(fileoffset)
		self.arity = Artutils.getExpArity(fileoffset)
	
	# arguments: return any arguments of this Program as a possibly-empty
	#            list.
	def arguments(self):
		return [Artutils.peekExpArg(self.fo, n) for n in range(1, self.arity+1)]
	
	def parent(self):
		# return a program object or None
		if not hasattr(self, "_parent"):
			p = Artutils.parentNode(self.fo)
			if not p == 0:
				self._parent = Program(p)
				#self._parent.children = [self]
			else:
				self._parent = None
		
		return self._parent
	
	def children(self):
		# return a (possibly empty) list of program objects
		if self.typ == Art.ExpApp:
			return getArgsMadeBy(self.fo, self.result())
		elif self.typ == Art.ExpConstUse:
			return [Program(Artutils.peekExpArg(self.fo, 0))]
		else:
			return []
	
	def result(self):
		# return a program object or None
		if not hasattr(self, "_result"):
			r = Artutils.peekResult(self.fo)
			if r == 0 or r == self.fo:
				self._result = None
			else:
				self._result = Program(r)
		
		return self._result
	
	def name(self):
		# return a string
		if not hasattr(self, "_trace"):
			self._trace = Artutils.traceFromFO(self.fo, 0, 5)
		
		return self._trace.expr	

# makeProgramFromString: make a Program from the given string, with the given
#                        global state
# commented out until we actually need it
#def makeProgramFromString(string, state):
	# this function is actually not correctly implemented right now.
	# no matter what the string is, it will just return the offset of the
	# use of the function 'main' in the trace state.hatfile.
#	if hasattr(state, "hatfile"):
#		return Program(Artutils.findMainUse(True))
#	else:
#		raise Exception("You can't run a program with no file open!")

# class State: holds the state of a computer. Provides the environment for
# executing programs.
# right now, this is a completely unnecessary dummy class
class State(object):
	def import_file(self, filename):
		print "Importing file", repr(filename), "!"
		f = open(filename)
		Artutils.openHatFile("Test", filename)
		self.hatfile = filename
	
	# default_program: return a program object to use when the user doesn't
	# specify one
	def default_program(self):
		return Program(Artutils.findMainUse(True))

