#!/usr/bin/python

import Artutils
import Art

import trace_interpret

import os.path # for the file-handling bits

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
		# subexps: right now we have a special case to find the subexps
		# of a basic expression, because the C function won't let us,
		# and everything else just calls the C. this is not quite
		# correct, because there are certain things that are not basic
		# values but still don't have subexpressions, but we don't deal
		# with those things right now. however, regardless of
		# correctness, it might make more sense in the future to switch
		# the type of special-casing: only call peekExpArg if our typ
		# meets certain conditions which are known to work, and
		# otherwise don't.
		#print "about to find subexps of", self.name()
		if isBasicExp(self.typ):
			se = []
		else:
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
		
		#print "parent of", self, "is", self._parent
		
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
	
	def definition(self):
		# return a program object or None
		if not hasattr(self, "_definition"):
			if self.typ == Art.ExpConstUse or self.typ == Art.ExpValueUse:
				self._definition = Program(Artutils.peekExpArg(self.fo, 0))
			else:
				self._definition = None
		
		return self._definition
	
	def name(self):
		#print "finding the name of a program object"
		
		# return a string
		if not hasattr(self, "_data"):
			if isExp(self.typ):
				#print "about to call Artutils.traceFromFO on fileoffset", self.fo
				self._data = Artutils.traceFromFO(self.fo, 0, 5)
				#print "Artutils.traceFromFO returned", self._data
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
		
		#print "have the data structure that holds the name"
		
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
	
	# subNodesFrom(source): find subnodes of node that are before the given
	# source in the result/parent graph, including the source.
	def subNodesFrom(source):
		#print "finding subnodes from", source
		
		sp = source.parent()
		
		#print "the parent of", source, "is", sp
		
		if sp != node:
			#print "the parent of", source, "is not", node, "!"
			# this might happen if subNodesFrom is called on the
			# result of node, which was actually created by a child
			# call from node.
			if sp is not None:
				res = subNodesFrom(sp)
			else:
				res = ([], [])
		elif source.typ == Art.ExpConstUse or source.typ == Art.ExpValueUse:
			#print source, "is a use!"
			res = ([source], [source.definition()])
		else:
			exps = [source] # include the source in the results
			defs = []
			for s in source.subexps():
				e, d = subNodesFrom(s)
				exps.extend(e)
				defs.extend(d)
			#print "subnodes of", source, ":", (exps, defs)
			res = (exps, defs)
		#print "subnodes from", source, "are", res
		return res
	
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

def isBasicExp(tag):
	return tag >= Art.ExpChar and tag <= Art.ExpDouble

# two file classes, to abstract over the difference between hat files and
# python files
class HatFile(object):
	def __init__(self, filename):
		self.filename = filename
		self.isOpen = False # "open" includes "resumed" here
	
	# open: open the file for the first time.
	def open(self):
		if not self.isOpen:
			Artutils.openHatFile("Sombrero", self.filename)
			self.isOpen = True
	
	# suspend: switch away from this file, but be ready to reopen it.
	def suspend(self):
		if self.isOpen:
			Artutils.closeHatFile()
			self.isOpen = False
	
	# resume: come back to this file after it has been suspended, but not
	# closed.
	def resume(self):
		if not self.isOpen:
			Artutils.openHatFile("Sombrero", self.filename)
			self.isOpen = True
	
	# close: close this file without the intention of coming back to it.
	def close(self):
		if self.isOpen:
			Artutils.closeHatFile()
			self.isOpen = False
	
	# name: return a string to identify this file in menus and such.
	def name(self):
		return self.filename

class PythonFile(object):
	def __init__(self, filename):
		self.filename = filename
		self.tracename = os.path.splitext(self.filename)[0] + ".hat"
		self.isOpen = False # "open" includes "resumed" here
	
	def open(self):
		if not self.isOpen:
			print "Opening Python file", self.filename
			trace_interpret.trace_file(self.filename)
			print "Done interpreting file, about to open trace"
			Artutils.openHatFile("Sombrero", self.tracename)
			self.isOpen = True
	
	def suspend(self):
		if self.isOpen:
			Artutils.closeHatFile()
			self.isOpen = False
		# we close the hat file, but our functiondefs stay in the
		# environment
	
	def resume(self):
		if not self.isOpen:
			Artutils.openHatFile("Sombrero", self.tracename)
			self.isOpen = True
	
	def close(self):
		if self.isOpen:
			Artutils.closeHatFile()
			self.isOpen = False
	
	def name(self):
		return self.filename

# class State: holds the state of a computer. Provides the environment for
# executing programs.
# right now, this is a completely unnecessary dummy class
class State(object):
	def __init__(self):
		self.openFile = None # store the open file or None
		self.openFiles = []
	
	# open_file_pairs: return a list of (name, file) pairs.
	def open_file_pairs(self):
		return [(f.name(), f) for f in self.openFiles]
	
	def import_file(self, filename):
		#print "Importing file", repr(filename), "!"
		if filename.endswith(".hat"):
			f = HatFile(filename)
		elif filename.endswith(".py"):
			f = PythonFile(filename)
		else:
			raise Exception("The file '" + filename + "' has an \
			                 unknown type, and cannot be imported")
		
		f.open()
		self.openFiles.append(f)
		self.openFile = f
	
	def switch_to_file(self, f):
		if f in self.openFiles:
			if self.openFile is not None:
				self.openFile.suspend()
			f.resume()
			self.openFile = f
		else:
			raise Exception("The file '" + filename + "' can't be \
			                 traced because it hasn't been \
			                 imported yet!")
	
	# default_program: return a program object to use when the user doesn't
	# specify one
	def default_program(self):
		return Program(Artutils.findMainUse(True))

