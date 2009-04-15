#!/usr/bin/python

import _ast
import Recorder

# trace_utils.py: holds miscellaneous utility functions that the tracer users.
# this file is useful to have because if the utility functions are in the files
# that do the work, then we get import circularities because both of the work
# files need to load the utility functions before either of them is
# initialized. we could also add an init<modulename> function, but this way
# seems simpler.

# lazy_lambda: generalized lazy evaluation. takes a thunk and evaluates it once
# no matter how many times it's called. I'm making it accessible by call rather
# than by access because the idea of calling a lazy object is, in fact, to
# maybe perform an arbitrary procedure (rather than retrieve data in probably
# O(1) time), and I like being explicit about that.
class lazy_lambda(object):
	def __init__(self, thunk):
		self.thunk = thunk
	
	def __call__(self):
		if hasattr(self, 'val'): # could also be try: ..val.. and then
			return self.val  # catch nameerror, but might as well
		else:			 # not break *all* the rules
			self.val = self.thunk()
			return self.val # del self.thunk?

# Maybe there should be a base class for the next two classes. Maybe even an
# abstract one?
# The next two classes deal with traced objects that can be accessed after they
# are created. They abstract over the difference between a ConstDef/ConstUse
# pair and a Variable/ValueUse pair.
class ConstDef(object):
	def __init__(self, context, var):
		self.obj = Recorder.makeValue(context, var)
	def makeAccess(self, parent):
		return self.obj

class Variable(object):
	def __init__(self, module, begin, end, fixity, arity, name, local):
		self.obj = Recorder.makeFunction(self, name, [str(i) for i in range(1, arity)])
	def makeAccess(self, parent):
		return self.obj

# This class is a general variable that needs no work to be accessed.
class Accessible(object):
	def __init__(self, parent, obj):
		self.source = parent
		self.obj = obj
	def makeAccess(self, parent, name, val):
		return Recorder.makeReference(parent,
					      self.source,
					      name,
					      val)

# Param is also a trace object that can be put in an environment. It deals with
# things that are already evaluated and dont' actually need a trace to be
# written, but need to look like other variables - parameters passed to
# functions
class Param(object):
	def __init__(self, trace):
		self.trace = trace
	def makeAccess(self, parent, use):
		return self.trace # LAME. But this is Hat's doing, and it will
		             # take some thought to understand or change.

class traced_function(object):
	def __init__(self, args, body):
		self.args = args # args and body are both ASTs.
		self.body = body

# the environment stores pairs of (value, accessable trace object)
frames = [dict()] # no builtins - have to handle them specially
def lookup(name):
	#print "lookup called on", name
	for i in xrange(len(frames)-1, -1, -1):
		#print "lookup iterating on frame", i
		try:
			res = frames[i][name]
			#print "lookup returning", res
			return res
		except KeyError:
			continue
	#print "lookup: couldn't find", name, "in the frames!"
	raise NameError, ("Couldn't find '%s'!" % (name,))

# AAAAH! assign doesn't have correct Python semantics! (Should only look in the
# innermost frame unless the variable has been marked global, I think. This
# should be checked (or made irrelevant :-))
def assign(name, val): # val is a pair of (value, trace)
	#print "assign: called on", (name, val)
	frames[-1][name] = val # no global statements yet

# store already-written atoms for primitives
_prims = dict()
import types

# builtins is special, because I can't think of a better way right now
#builtins = lazy_lambda(lambda: mkModule('__builtins__', "__builtins__.py", False))
builtins = Recorder.top_level

# lookup_primitive: special lookup function for builtins
def lookup_primitive(name):
	try:
		(val, atom) = _prims[name]
	except KeyError:
		try:
			val = __builtins__.__dict__[name]
		except KeyError:
			raise NameError, ("Couldn't find %s!" % (name,))

		if isinstance(val, types.BuiltinFunctionType):
			atom = Recorder.makeFunction(builtins, name, [str(i) for i in range(1, arity)])
		else:
			atom = Recorder.makeValue(Recorder.top_level, val)
	
	return (val, atom)

def access_primitive(name, parent):
	(val, atom) = lookup_primitive(name)
	
	return (val, atom)

# access: access a variable by name.
# QUESTION: should this just be in eval_name in trace_funcs.py?
# name is a string, parent is a trace node
# returns a pair of (value, trace of access)
def access(name, parent):
	try:
		(val, traceobj) = lookup(name)
	except NameError:
		return access_primitive(name, parent)
	
	use = traceobj.makeAccess(parent, name, val)
	return (val, use)

# lazy_writer: used to generate the traces of primitive functions. will write a
# variable name to the trace *if* the name is actually used.
# note: should probably switch between variables and Consts for arity !=0 and 0
def lazy_writer(name, arity):
	return lazy_lambda(lambda: Recorder.makeFunction(Recorder.top_level, name, [str(i) for i in range(1, arity)]))

def mkAppn(parent, use, func, num, *args):
	return Recorder.makeComputation(parent, func, list(args))

# ast_indented_str: hackish and still loops, but gives pretty good output.
# returns a string that contains the internal newlines and spacing to give nice
# output, but doesn't end in a newline, and doesn't start with spacing (so it
# assumes that you're going to print it with the cursor already at the indent
# column - I do this by starting at indent 0).
def ast_indented_str(ast, indent):
	if isinstance(ast, _ast.AST): # all ASTs have a _fields attribute
		if ast._fields != None:
			newindent = indent + len(ast.__class__.__name__) + 1 # +1 for the parentheses
			subs = (ast_indented_str(ast.__dict__[x], newindent) for x in ast._fields)
			return (ast.__class__.__name__
			        + "(" + ("\n" + (" " * newindent)).join(subs) + ")")
		else:
			return ast.__class__.__name__
	elif isinstance(ast, list): # some attributes are lists of ASTS
		newindent = indent + 1
		f = lambda ast: ast_indented_str(ast, newindent)
		return "[" + ("\n" + (" " * newindent)).join(map(f, ast)) + "]" # switch map to generator?
	elif ast == None: # some optional attributes are None
		return "None"
	else:
		return str(ast) # making this repr would have interesting effects

# dump_saved_environment: print the names being saved for new function runs.
# this entire system is a terrible hack, and should be be taken out and
# replaced with something good.
def dump_saved_environment():
	print "Number of frames:", len(frames)
	print "Environment size:", len(frames[0])
	
	print "Saved environment:"
	for (name, (val, trace)) in frames[0].iteritems():
		if val.__class__ == traced_function:
			print "Traced function", name, "with args", \
			      ast_indented_str(val.args, 26+len(name)), ":"
			print ast_indented_str(val.body, 0)
		else:
			print "Unsaved variable:", name
	
	# XXX: AAAAH! MORE INSANTIY! The saved environment for future
	# computations is kept in a global variable, instead of being passed
	# into and out of trace_... like it should be. (*Those* functions, of
	# course, could put it into a global variable and retrieve the results
	# later, but the interface should probably take arguments and return
	# values.)
	for name in frames[0].keys(): # can't use iteritems() for deleting.
		if frames[0][name][0].__class__ != traced_function:
			del frames[0][name]
	
	print "Final environment size:", len(frames[0])

