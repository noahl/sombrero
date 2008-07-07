#!/usr/bin/python

# trace-allcall-transform: another revision of the Python tracer
# basic idea: Python includes hooks for tracing the evaluation of every
# statement, function call, and function return. we trace code by transforming
# the AST so that all of the built-in operations are replaced by calls. this is
# efficient because any tracing scheme will involve making a call for each
# traced operation anyway, so we're not losing anything, and using the built-in
# tracing makes it very convenient. this is nice because it eliminates a lot of
# the infrastructure an interpreter needs, like environments and such things.
# also gives corrent Python semantics for free for a lot of things.

# the ast (no underscore) module is pretty indispensable for this method, so
# this file needs Python 2.6 or better. because of this, I'm going to write the
# rest of it using cool Python 2.6 features too, like with-statements.
from ast import *
from Trace import * # everything in here is prefixed with "hat_" or "mk" anyway


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


# store already-written atoms for primitives
_prims = dict()
import types
# builtins is special, because I can't think of a better way right now
builtins = lazy_lambda(lambda: mkModule('__builtins__', "__builtins__.py", False))
# lookup_primitive: special lookup function for builtins
def lookup_primitive(name):
	try:
		(val, atom) = _prims[name]
	except KeyError:
		try:
			val = __builtins__.__dict__[name]
			if isinstance(val, types.BuiltinFunctionType):
				atom = mkVariable(builtins(),
				                  0, # begin
				                  0, # end
				                  0, # fixity
				                  -1, # arity
				                  name, # name
				                  False) # local
			else:
				atom = mkVariable(builtins(),
				                  0, 0, 0, 0,
				                  name, False)
		except KeyError:
			raise NameError, ("Couldn't find %s!" % (name,))
	
	return (val, atom)

def access_primitive(name, parent):
	(val, atom) = lookup_primitive(name)
	
	return (val, mkValueUse(parent, 0, atom))


# lazy_writer: used to generate the traces of primitive functions. will write a
# variable name to the trace *if* the name is actually used.
# note: should probably switch between variables and Consts for arity !=0 and 0
def lazy_writer(name, arity):
	return lazy_lambda(lambda: mkVariable(module, 0, 0, 0, arity, name, False))

def mkAppn(parent, use, func, num, *args):
	x = len(args) # don't know how good the Python compiler is
	              # (or what the cost of getting a tuple's length is)
	if x == 1:
		return mkApp1(parent, use, func, *args)
	elif x == 2:
		return mkApp2(parent, use, func, *args)
	elif x == 3:
		return mkApp3(parent, use, func, *args)
	elif x == 4:
		return mkApp4(parent, use, func, *args)
	elif x == 5:
		return mkApp5(parent, use, func, *args)
	else:
		raise Exception, "Unhandled case in mkAppn!"

# UnimplementedException: raised when the transformer can't handle some feature
# of standard Python.
class UnimplementedException(Exception):
	pass

# gensym_series: make a gensym maker. I shouldn't need this function.
def gensym_series(start = 0):
	while 1:
		yield "_gensym__"+str(start)
		start = start + 1

# gensym: make names that probably won't be used by anything else.
gensym = gensym_series().next

# parent: the name that will always hold the parent of an expression
parent = ""

# modsym: the name of the current module
modsym = ""

# *Maker functions obey the following conventions:
#   - the functions take ASTs as their arguments and return ASTs as their
#     results, except for lineno and col_offset

def variableMaker(lineno, col_offset, *args):
	return Call(lineno = lineno, col_offset = col_offset,
	            func = Name("mkVariable", Load()),
	            args = args,
	            keywords = [], starargs = None, kwargs = None)

def constDefMaker(lineno, col_offset, *args):
	return Call(lineno = lineno, col_offset = col_offset,
	            func = Name("mkConstDef", Load()),
	            args = args,
	            keywords = [], starargs = None, kwargs = None)

def intMaker(lineno, col_offset, *args):
	return Call(lineno = lineno, col_offset = col_offset,
	            func = Name("mkInt", Load()),
	            args = args,
	            keywords = [], starargs = None, kwargs = None)

def loadMaker(lineno, col_offset, parent, node):
	return Call(lineno = lineno, col_offset = col_offset,
	            func = Name("_handleLoad", Load()),
	            args = [parent, node],
	            keywords = [], starargs = None, kwargs = None)

# call_expr: call an expression function (the result of transforming an
# expression) with the given parent. parent is an ast
def call_expr(parent, expr):
	#print "call_expr called on", parent, expr
	return expr(parent)

# _handleLoad: part of the runtime
def _handleLoad(parent, wrapped):
	(val, constdef) = wrapped
	return (val, mkConstUse(parent, 0, constdef))

# transformed code obeys the following conventions:
#   - all values are (value, trace) pairs
#   - all transformed expressions are function calls
class TraceTransformer(NodeTransformer):
	def visit_Assign(self, node):
		if len(node.targets) > 1:
			raise UnimplementedException("Assignment to multiple \
			                          variables is not supported!")
		#print "visit_Assign called on", node
		variable = gensym()
		tracevar = gensym()
		valval = gensym()
		valtrace = gensym()
		return [
		Assign( # make a new variable and assign it to variable
		  lineno = node.lineno, col_offset = node.col_offset,
		  targets = [Name(variable, Store())],
		  value = variableMaker(Name(modsym, Load()), Num(0), Num(0),
		                        Num(0), Num(0), variable,
		                        Name("True", Load()))
		  ),
		Assign( # make a new ConstDef and assign it to tracevar
		  lineno = node.lineno, col_offset = node.col_offset,
		  targets = [Name(tracevar, Store())],
		  value = constDefMaker(Name(parent, Load()),
		                        Name(variable, Load()))
		  ),
		Call( # call entResult on the tracevar
		  lineno = node.lineno, col_offset = node.col_offset,
		  func = Name("entResult", Load()),
		  args = (Name(tracevar, Load()), Num(0)),
		  keywords = [], starargs = None, kwargs = None
		  ),
		Assign( # run the right hand side, store to (valval, valtrace)
		  lineno = node.lineno, col_offset = node.col_offset,
		  targets = [Tuple([Name(valval, Store()),
		                    Name(valtrace, Store())],
		                   Store())],
		  value = call_expr(Name(tracevar, Load()),
		                    self.visit(node.value))
		  ),
		Assign( # assign (valval, tracevar) to the original targets
		  lineno = node.lineno, col_offset = node.col_offset,
		  targets = node.targets,
		  value = Tuple([Name(valval, Load()),
		                 Name(tracevar, Load())],
		                Load())
		  ),
		Call( # call resResult on the tracevar with valtrace and 0
		  lineno = node.lineno, col_offset = node.col_offset,
		  func = Name("resResult", Load()),
		  args = (Name(tracevar, Load()),
		          Name(valtrace, Load()),
		          Num(0)),
		  keywords = [], starargs = None, kwargs = None
		  )
		]
	
	def visit_Name(self, node):
		if node.ctx.__class__ is Load:
			def ast(parent):
				return loadMaker(node.lineno,
				                 node.col_offset,
				                 parent,
				                 node)
			return ast
		else:
			raise Exception("Non-load name %s visited!" % str(node))
	def visit_Num(self, node):
		def ast(parent):
			res = Tuple([Num(node.n),
			              intMaker(node.lineno,
			                       node.col_offset,
			                       Name(parent, Load()),
			                       0,
			                       Num(node.n))],
			             Load())
			#print "ast from visit_Num returning", res
			return res
		#print "visit_Num returning", ast
		return ast
	
	def generic_visit(self, node):
		#print "Visiting unexpected node %s!" % str(node)
		for n in iter_child_nodes(node):
			self.visit(n)
		return node
	


# ast_indented_str: hackish and still loops, but gives pretty good output.
# returns a string that contains the internal newlines and spacing to give nice
# output, but doesn't end in a newline, and doesn't start with spacing (so it
# assumes that you're going to print it with the cursor already at the indent
# column - I do this by starting at indent 0).
def ast_indented_str(ast, indent):
	if isinstance(ast, AST): # all ASTs have a _fields attribute
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

def load_file(filename):
	with open(filename) as f:
		return compile(f.read(), filename, 'exec', PyCF_ONLY_AST)

# HAT-SPECIFIC WEIRDNESS: all programs have to appear to be in a module called
# 'Main', with a top-level variable called 'main' of arity 0 that does all the
# work.
def trace_file(filename):
	print "Tracing file ", filename
	
	mod = load_file(filename)

	print "Input AST:\n", ast_indented_str(mod, 0)
	
	assert mod.__class__ == Module
	
	mod = TraceTransformer().visit(mod)
	
	print "Transformed AST:\n", ast_indented_str(mod, 0)
		
	# use everything but the last extension
	import os.path
	hat_Open(os.path.split(filename)[0]
	         + os.path.splitext(os.path.split(filename)[1])[0])
	
	global modsym
	global parent
	module = mkModule('Main', filename, True)
	modsym = "module"
	variable_main = mkVariable(module, 1, 3, 0, 0, "main", True)
	definition_main = mkConstDef(mkRoot(), variable_main)
	parent = "definition_main"
	use_main = mkConstUse(0, 0, definition_main)
	
	# right now in the trace, the program was started and main was called
	# now, execution enters main
	entResult(definition_main, 0)
		
	print "Program Terminal:\n"
	try:
		# run the program in mod with parent definition_main
		exec compile(Module(mod.body[:-1]), filename, 'exec')
		assert mod.body[len(mod.body)-1].__class__ == Expr
		res = eval(compile(Expression(mod.body[len(mod.body)-1].value), filename, 'eval'))
		resResult(definition_main, res[1], 0)
	finally:
		hat_Close()

def _main():
	import sys
	
	for filename in sys.argv[1:]:
		trace_file(filename)

if __name__ == '__main__':
	_main()
