#!/usr/bin/python

# trace-interpret.py: interpret a Python file while recording its execution
# through the Recorder interface

import _ast
import Recorder

from trace_utils import ast_indented_str, dump_saved_environment
from trace_funcs import *

# note: exec_stmts is currently implemented as a giant dispatch, but see the
# comment just before tracing_ast in translate.py for an alternate
# implementation that might be faster and more efficient.

# CURRENT THOUGHT:
# there are four stages of computation that we care about:
# AST => Trace of Expressions => Trace of Results => Results
#   (Results might actually be parallel to the tracing)
# exec_stmts right now does all of this, but it's not working very well for
# built-in laziness (and, or, if) because we can't get the traces of the
# expressions. It might be better to split this process into two functions,
# a :: AST => Trace of Expressions and
# b :: Trace of Expressions => (Trace of Results, Results)

# exec_stmts: run some code and generate a trace of the result.
# ast is an _ast.AST. parent is a Trace.FileOffset.

# exec_stmts, and all of its subroutines, trace in two steps: first, they
# write the *unevaluated* trace of their argument to the file, and they create
# a thunk which, if called, will return a pair of (result, trace of result),
# containing the final result of their computation. Then, they return a pair of
# (thunk, unevaluated trace).

# The rule for updating is that whoever calls entResult on a node is
# responsible for calling resResult on it later (whenever subroutines return?)
# also, you *must* call entResult before resResult, even if you don't care
# about marking it as entered, because entResult and resResult correspond to
# push and pop in the hat stack. (The alternative would be to use lower-level
# functions, but that would require making Python wrappers, and this works.
# also, we probably *should* do this anyway to produce nice results).

# NOTE: entResult should ALWAYS be called in the THUNK, NOT by whatever is
# using the thunk. The reason is that not everything needs entResult called,
# and in fact, calling entResult on, say, a ConstUse will corrupt the file and
# result in mysterious segmentation faults in the viewing tools.

# More generally: entResult (and resResult) should ALWAYS be called by WHATEVER
# CREATED THE THING THAT THEY ARE BEING CALLED ON. That is the only object that
# knows whether it is appropriate to call them or not. Nothing else can.

# a RetVal marks a call to return, which means it can interrupt a sequence of
# statements before they reach the end
class RetVal(object):
	def __init__(self, val):
		self.val = val # val is (value, trace)
parents = [] # parents: the stack of parents
# statements return either None or a RetVal.
def exec_stmts(asts):
	for stmt in asts:
		res = exec_stmt(stmt)
		if res.__class__ == RetVal:
			return res
	return None # Do *NOT* return a RetVal here, because that could stop an
	            # enclosing exec_stmts before it finishes.

exectable = {
	_ast.Expr: exec_expr,
	_ast.Assign: exec_assign,
	_ast.FunctionDef: exec_functiondef,
	_ast.If: exec_if,
	_ast.Print: exec_print,
	_ast.Return: exec_return
}

def exec_stmt(ast):
	assert isinstance(ast, _ast.stmt)

	try:
		executor = exectable[ast.__class__]

		res = executor(ast)
		
		if res.__class__ == RetVal: # might return, but not necessarily
			return res
	except ex:
		raise Exception("Unrecognized AST node %s!" % (ast.__class__.__name__,))
	
	return None

evaltable = {
	_ast.BinOp:   eval_binop,
	_ast.BoolOp:  eval_boolop,
	_ast.Call:    eval_call,
	_ast.Compare: eval_compare,
	_ast.Name:    eval_name,
	_ast.Num:     eval_num,
	_ast.Str:     eval_str,
	_ast.UnaryOp: eval_unaryop
}

def eval_tracing(ast):
	assert isinstance(ast, _ast.expr)

	try:
		evaluator = evaltable[ast.__class__]
	except ex:
		res = (ex,
		       Recorder.makeError(parents[-1], ex))
		return res

	# you caught us in the middle of changing interfaces!
	# this is so embarrassing. please look back later. *blush*
	if callable(evaluator):
		res = evaluator(ast)
		
		def wrapper():
			try:
				result = res[0]()
			except Exception, ex:
				# the next line is wrong because it
				# gives the wrong parent. (unless you
				# count on the trace function *not*
				# catching errors, which makes me
				# nervous.
				result = (ex,
					  Recorder.makeError(
						parents[-1], str(ex)))
			return result
	else:
		# 'evaluator' is a class.
		
		# Make the trace
		subs = evaluator.subexpressions()
		subs = [eval_tracing(s) for s in subs]
		trace =  evaluator.makeTrace([s[1] for s in subs])
		
		def wrapper():
			# Enter the trace
			parents.append(trace)
			Recorder.enterComputation(trace)
			try:
				# Evaluate the expression
				result = evaluator.eval(subs)
			except ex:
				result = (ex,
				       Recorder.makeError(trace, ex))
                        finally:
				Recorder.finishComputation(trace, result[1])
				parents.pop()
	
			return (res, trace)
		res = (wrapper, trace)
	
	
	return (wrapper, res[1])

def load_file(filename):
	f = open(filename) # unsafe code here because I was making it work in Python 2.5
	mod = compile(f.read(), filename, 'exec', _ast.PyCF_ONLY_AST)
	f.close()
	return mod

def trace_file(filename):
	print "Tracing file ", filename
	
	mod = load_file(filename)

	print "Input AST:\n", ast_indented_str(mod, 0)
	
	assert mod.__class__ == _ast.Module

	# use everything but the last extension
	import os.path
	name = os.path.split(filename)[0] + "/" \
	       + os.path.splitext(os.path.split(filename)[1])[0]
	
	parents.append(Recorder.top_level)

	res = None
	
	print "Program Terminal:\n"
	try:
		# run the program in mod with parent definition_main
		exec_stmts(mod.body[:-1])
		if mod.body[-1].__class__ == _ast.Expr:
			res = eval_tracing(mod.body[-1].value)
			res = res[0]()
		else:
			exec_stmt(mod.body[-1])
			res = primitive_io()
		print "Overall result:" + str(res)

		if len(parents) != 0:
			print "Non-fatal error: parents left after module finished!"
	except ex:
		print "Top-level exception!"
		res = (ex,
		       Recorder.makeError(Recorder.top_level, ex))
	finally:
		Recorder.set_top_level_program(res[1])
		parents.pop()
		pass
	
	print "End program terminal"
	
	# XXX: AAAAH! THIS IS A TERRIBLE HACK THAT SHOULD BE FIXED! This code
	# scans the top-level environment for any traced_function objects and
	# saves them for future runs. It is important to save traced function
	# ASTs after we interpret a file so that we can evaluate future
	# interactively-interpreted expressions with them. However, this is not
	# a correct implementation of Python semantics, because it does not
	# save top-level non-function variables and it does not do anything
	# useful with closures (although that's not entirely the fault of this
	# section of the code - class traced_function could be modified to keep
	# an environment around, which should somewhat take care of that,
	# except that then the closure environments would need to be saved for
	# retracing too). Those defects should be fixed.
	# Alternatively, we could not bother saving the ASTs for anything, but
	# put all of the traces for one run of Sombrero into one trace file,
	# which would just have multiple entry points. This would be an elegant
	# solution to this problem, except that ASTs really *should* be saved
	# so that the user can use them later.
	# A third option, of course, is to change from an interpreter to a
	# translater, translate traced function definitions as objects that
	# trace themselves, and let Python handle the environments. This would
	# be great except for the effort required to make it work.
	# Ideally all three of these things would be done - ASTs would be saved
	# so the user could dump his or her function definitions to a file at
	# the end of a sombrero session, this would be a translater rather than
	# an interpreter, and we would save everything with maximum efficiency,
	# either in one big file or in several little files with cross-file
	# references.
	
	dump_saved_environment()
	
def _main():
	import sys
	
	for filename in sys.argv[1:]:
		trace_file(filename)

if __name__ == '__main__':
	_main()
