#!/usr/bin/python

import Artutils
import Art

# the Program class represents a traced program
# this implementation returns information from a Hat trace file

# keep a dictionary of all the programs
_programs = {}

class Program(object):
	def __new__(cls, fileoffset):
		# make sure there is only one Program for every fileoffset
		
		if not (isinstance(fileoffset, int) or isinstance(fileoffset, long)):
			raise Exception("Program created with invalid offset \
			                 type %s" % str(fileoffset.__class__))
		
		try:
			return _programs[fileoffset]
		except KeyError:
			p = super(Program, cls).__new__(cls, fileoffset)
			p.fo = fileoffset
			_programs[fileoffset] = p
			return p
	
	def __init__(self, fileoffset):
		self.typ = Artutils.getNodeType(fileoffset)
		self.arity = Artutils.getExpArity(fileoffset)
	
	def subexps(self):
		se = [Program(Artutils.peekExpArg(self.fo, n)) for n in range(0, self.arity+1)]
		#print "the subexps of", self.name(), "are", se
		return se
	
	def parent(self):
		# return a program object or None
		if not hasattr(self, "_parent"):
			p = Artutils.parentNode(self.fo)
			if not p == 0:
				self._parent = Program(p)
			else:
				self._parent = None
		
		return self._parent
	
	def children(self):
		# return a (possibly empty) list of program objects
		#if self.typ == Art.ExpApp:
		#	return argsMadeBy(self, self.result())
		#elif self.typ == Art.ExpConstUse:
		#	return [Program(Artutils.peekExpArg(self.fo, 0))]
		#elif self.typ == Art.ExpConstDef:
		#	return argsMadeBy(self, self.result())
		#else:
		#	return []
		(e, d) = subNodes(self)
		return e
	
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
		if not hasattr(self, "_data"):
			if isExp(self.typ):
				self._data = Artutils.traceFromFO(self.fo, 0, 5)
				if self.typ == Art.ExpConstUse:
					self._data.expr = self._data.expr + " (use)"
				elif self.typ == Art.ExpConstDef:
					self._data.expr = self._data.expr + " (def)"
				elif self.typ == Art.ExpValueUse:
					self._data.expr = self._data.expr + " (use)"
			elif isAtom(self.typ):
				self._data = Artutils.readAtomAt(self.fo)
				if self.typ == Art.AtomVariable:
					self._data.idname = self._data.idname + " (var)"
			else:
				raise Exception("Can't get data for node type " + str(self.typ))
		
		if isinstance(self._data, Artutils.Trace):
			return self._data.expr
		elif isinstance(self._data, Artutils.Ident):
			return self._data.idname
		else:
			raise Exception("Don't understand data " + str(self._data))
	
	__str__ = name
	__repr__ = name

def argsMadeBy(author, exp):
	# author and exp are Programs
	if not exp.parent() == author:
		return []
	else:
		args = [exp]
		for s in exp.subexps():
			args.extend(argsMadeBy(author, s))
		
		return args

# subNodes: return a tuple of
#   - expressions created by this one
#   - definitions accessed by this one
def subNodes(node):
	# based on traverseReduct in <hat-src>/hattools/HatExplore.hs
	#print "finding subNodes of", node
	def subNodesFrom(source):
		#print "finding subnodes from", source
		if source.parent() != node:
			#print "no subnodes from", source, "!"
			return ([], [])
		elif source.typ == Art.ExpConstUse:
			#print source, "is a constuse!"
			return ([], [source.result()]) # result gives the def
		elif source.typ == Art.ExpValueUse:
			#print source, "is a valueuse!"
			return ([], [Artutils.peekExpArg(source.fo, 0)])
		else:
			exps = [] # don't count source here - this gets an extra node
			defs = []
			for s in source.subexps():
				e, d = subNodesFrom(s)
				exps.append(s) # instead, catch nodes here
				exps.extend(e)
				defs.extend(d)
			#print "subnodes of", source, ":", (exps, defs)
			return (exps, defs)
	
	r = node.result()
	if r is not None:
		s = subNodesFrom(r)
	else:
		s = ([], [])
	#print "subNodes of", node, "are", s
	return s

# is*: these tag test functions should really be in the Art module (in C).
def isExp(tag):
	return tag >= Art.ExpApp and tag <= Art.ExpDoStmt

def isAtom(tag):
	return tag >= Art.AtomVariable and tag <= Art.AtomAbstract

def isValueExp(tag):
	return tag >= Art.ValueApp and tag <= Art.ConstDef

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
	def __init__(self):
		self.haveOpenFile = False # flag - do we have a file open or not?
		self.openfilenames = []
	
	def import_file(self, filename):
		#print "Importing file", repr(filename), "!"
		if filename.endswith(".hat"):
			Artutils.openHatFile("Test", filename)
			self.haveOpenFile = True
			self.openfilenames.append(filename)
			self.hatfile = filename
		else:
			raise Exception("The file '" + filename + "' has an \
			                 unknown type, and cannot be imported")
	
	def switch_to_file(self, filename):
		if filename in self.openfilenames:
			if self.haveOpenFile:
				Artutils.closeHatFile()
			Artutils.openHatFile(filename)
			self.hatfile = filename
		else:
			raise Exception("The file '" + filename + "' can't be \
			                 traced because it hasn't been \
			                 imported yet!")
	
	# default_program: return a program object to use when the user doesn't
	# specify one
	def default_program(self):
		return Program(Artutils.findMainUse(True))

