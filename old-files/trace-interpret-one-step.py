#!/usr/bin/python

import _ast
import numbers
from Trace import * # everything in here is prefixed with "hat_" or "mk" anyway

# note: exec_tracing is currently implemented as a giant dispatch, but see the
# comment just before tracing_ast in translate.py for an alternate
# implementation that might be faster and more efficient.

# CURRENT THOUGHT:
# there are four stages of computation that we care about:
# AST => Trace of Expressions => Trace of Results => Results
#   (Results might actually be parallel to the tracing)
# exec_tracing right now does all of this, but it's not working very well for
# built-in laziness (and, or, if) because we can't get the traces of the
# expressions. It might be better to split this process into two functions,
# a :: AST => Trace of Expressions and
# b :: Trace of Expressions => (Trace of Results, Results)

# our environment stores pairs of (value, trace).
frames = [__builtins__.__dict__, dict()]
def lookup(name):
	for i in xrange(len(frames)-1, -1, -1):
		try:
			return frames[i][name]
		except KeyError:
			continue
	raise NameError, ("Couldn't find '%s'!" % (name,))

def assign(name, val):
	for i in xrange(len(frames)-1, -1, -1):
		if name in frames[i]:
			frames[i][name] = val
			return
	frames[len(frames)-1][name] = val

# lazy_writer: used to generate the traces of primitive functions. will write a
# variable name to the trace *if* the name is actually used.
class lazy_writer(object):
	def __init__(self, name, arity):
		self.name = name
		self.arity = arity
		self.ref = None
	
	def __call__(self):
		global module
		
		if self.ref is not None:
			return self.ref
		else:
			print "Lazy-writing primitive '", self.name, "'"
			self.ref = mkVariable(module, 0, 0, 0, self.arity, self.name, False)
			return self.ref

# exec_tracing: run some code and generate a trace of the result.
# ast is an _ast.AST. parent is a Trace.FileOffset.
# exec_tracing, and all of its subroutines, obey this convention:
# they are called with an AST and a parent node. They return a pair of (value,
# trace). Both can be None if it's appropriate.
# The rule for updating is that whoever calls entResult on a node is
# responsible for calling resResult on it later (whenever subroutines return?)
# also, you *must* call entResult before resResult, even if you don't care
# about marking it as entered, because entResult and resResult correspond to
# push and pop in the hat stack. (The alternative would be to use lower-level
# functions, but that would require making Python wrappers, and this works.
# also, we probably *should* do this anyway to produce nice results).
def exec_tracing(ast, parent):
	assert isinstance(ast, _ast.AST)
	assert isinstance(parent, int) # int should be FileOffset here
	
	if ast.__class__ == _ast.Expr: # an Expr is a type of stmt.
		res = exec_tracing(ast.value, parent)
	elif ast.__class__ == _ast.Assign:
		res = traced_assign(ast, parent)
	elif ast.__class__ == _ast.BinOp:
		res = traced_binop(ast, parent)
	elif ast.__class__ == _ast.BoolOp:
		res = traced_boolop(ast, parent)
	elif ast.__class__ == _ast.If: # the stmt, not the expr
		res = traced_if(ast, parent)
	elif ast.__class__ == _ast.Name:
		res = traced_name(ast, parent)
	elif ast.__class__ == _ast.Num:
		res = traced_num(ast, parent)
	elif ast.__class__ == _ast.UnaryOp:
		res = traced_unaryop(ast, parent)
	else:
		raise Exception, "Unrecognized AST!"
	
	print ast_indented_str(ast, 0), "\nEvaluates To:\n", res[0]
	
	return res

def traced_assign(asn, parent):
	assert asn.__class__ == _ast.Assign
	
	val = exec_tracing(asn.value, parent)
	
	for name in asn.targets:
		assign(name.id, (val[0], mkProjection(parent, 0, val[1])))
	
	return (None, None) # what *should* the trace value here be?

primitive_add = lazy_writer("+", 2)
primitive_sub = lazy_writer("-", 2)
primitive_mul = lazy_writer("*", 2)
primitive_div = lazy_writer("//", 2) # only integers right now
def traced_binop(binop, parent):
	assert binop.__class__ == _ast.BinOp
	
	left = exec_tracing(binop.left, parent)
	right = exec_tracing(binop.right, parent)
	
	if binop.op.__class__ == _ast.Add:
		app = mkApp2(parent, 0, primitive_add(), left[1], right[1])
		res = (left[0] + right[0], mkInt(0, 0, left[0] + right[0]))
	elif binop.op.__class__ == _ast.Sub:
		app = mkApp2(parent, 0, primitive_sub(), left[1], right[1])
		res = (left[0] - right[0], mkInt(0, 0, left[0] - right[0]))
	elif binop.op.__class__ == _ast.Mult:
		app = mkApp2(parent, 0, primitive_mul(), left[1], right[1])
		res = (left[0] * right[0], mkInt(0, 0, left[0] * right[0]))
	elif binop.op.__class__ == _ast.Div:
		app = mkApp2(parent, 0, primitive_div(), left[1], right[1])
		res = (left[0] // right[0], mkInt(0, 0, left[0] // right[0]))
	else:
		raise Exception, "Unrecognized BinOp!"
	
	entResult(app, 0)
	resResult(app, res[1], 0)
	
	return res

primitive_and = lazy_writer("and", 2)
primitive_or = lazy_writer("or", 2)
def traced_boolop(boolop, parent):
	assert boolop.__class__ == _ast.BoolOp
	assert len(boolop.values) >= 2
	
	def and_reducer():
		# this loop uses two variables:
		#   prev is the result of the boolops up to the current one
		#   this is the next expression that needs to be boolop'd
		# the result will be in prev when the loop is done
		prev = exec_tracing(boolop.values[0], parent)
		
		if not prev[0]:
			return prev
		
		for this in boolop.values[1:]:
			ev = exec_tracing(this, parent)
			
			assert prev[0]
			if ev[0]:
				# 'and' returns its second argument if both are true, not True
				prev = (ev[0], mkApp2(parent, 0, primitive_and(), prev[1], ev[1]))
				entResult(prev[1], 0) # make entResult/resResult pairs for the Hat stack
				resResult(prev[1], ev[1], 0)
			else:
				res = (prev[0], mkApp2(parent, 0, primitive_and(), prev[1], ev[1]))
				entResult(res[1], 0)
				resResult(res[1], prev[1], 0)
				return res
		else:
			return prev
		
		raise Exception, "At the end of and_reducer!"
	
	def or_reducer():
		prev = exec_tracing(boolop.values[0], parent)
		
		if prev[0]:
			return prev
		
		for this in boolop.values[1:]:
			ev = exec_tracing(this, paremt)

			assert not prev[0]
			if ev[0]:
				# or returns its second argument if the first is false
				res = (ev[0], mkApp2(parent, 0, primitive_or(), prev[1], ev[1]))
				entResult(res[1], 0)
				resResult(res[1], ev[1], 0)
				return res
			else:
				prev = (ev[0], mkApp2(parent, 0, primitive_or(), prev[1], ev[1]))
				entResult(prev[1], 0)
				resResult(prev[1], ev[1], 0)
		else:
			return prev
		
		raise Exception, "At the end of or_reducer!"
	
	if boolop.op.__class__ == _ast.And:
		return and_reducer()
	elif boolop.op.__class__ == _ast.Or:
		return or_reducer()
	else:
		raise Exception, "Unknown boolop!"

def traced_if(exp, parent):
	assert exp.__class__ == _ast.If
	
	cond = exec_tracing(exp.test, parent)
	
	trace = mkIf(parent, 0, cond[1])

def traced_name(name, parent):
	assert name.__class__ == _ast.Name
	
	return lookup(name.id) # the lookup will return a (name, trace) pair.

def traced_num(num, parent):
	assert num.__class__ == _ast.Num
	assert isinstance(num.n, int)
	
	return (num.n, mkInt(parent, 0, num.n))

primitive_not = lazy_writer("not", 1)
primitive_true = lazy_writer("True", 0)   # looks like there's no mkBool, so...
primitive_false = lazy_writer("False", 0)
def traced_unaryop(unaryop, parent):
	assert unaryop.__class__ == _ast.UnaryOp
	
	operand = exec_tracing(unaryop.operand, parent)
	
	if unaryop.op.__class__ == _ast.Not:
		app = mkApp1(parent, 0, primitive_not(), operand[1])
		entResult(app, 0)
		if operand[0]:
			res = (False, primitive_false())
		else:
			res = (True, primitive_true())
		resResult(app, res[1], 0)
		return res
	else:
		raise Exception, "Unsupported UnaryOp!"

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

def load_file(filename):
	with open(filename) as f:
		return compile(f.read(), filename, 'exec', _ast.PyCF_ONLY_AST)

# HAT-SPECIFIC WEIRDNESS: all programs have to appear to be in a module called
# 'Main', with a top-level variable called 'main' of arity 0 that does all the
# work.
def trace_file(filename):
	mod = load_file(filename)

	print "Input AST:\n", ast_indented_str(mod, 0)
	
	assert mod.__class__ == _ast.Module

	# use everything but the last extension
	import os.path
	hat_Open(os.path.split(filename)[0]
	         + os.path.splitext(os.path.split(filename)[1])[0])
	
	global module
	module = mkModule('Main', filename, True)
	variable_main = mkVariable(module, 1, 3, 0, 0, "main", True)
	definition_main = mkConstDef(0, variable_main)
	use_main = mkConstUse(0, 0, definition_main)
	
	# right now in the trace, the program was started and main was called
	# now, execution enters main
	entResult(definition_main, 0)
		
	print "Program Terminal:\n"
	try:
		# run the program in mod with parent definition_main
		for stmt in mod.body[:-1]:
			exec_tracing(stmt, definition_main)
		res = exec_tracing(mod.body[len(mod.body)-1], definition_main)
		resResult(definition_main, res[1], 0)
	finally:
		hat_Close()

def _main():
	global filename # does this really have to be global?
	
	import sys
	
	filename = sys.argv[1]
	
	trace_file(filename)

if __name__ == '__main__':
	_main()
