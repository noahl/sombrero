#!/usr/bin/python

import _ast
from Trace import * # everything in here is prefixed with "hat_" or "mk" anyway
import sys # for stdout, for eval_print

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
# The next two classes deal with traced object that can be accessed after they
# are created. They abstract over the difference between a ConstDef/ConstUse
# pair and a Variable/ValueUse pair.
class ConstDef(object):
	def __init__(self, context, var):
		self.obj = mkConstDef(context, var)
	def makeAccess(self, parent, use):
		return mkConstUse(parent, use, self.obj)

class Variable(object):
	def __init__(self, module, begin, end, fixity, arity, name, local):
		self.obj = mkVariable(module, begin, end,
		                      fixity, arity, name, local)
	def makeAccess(self, parent, use):
		return mkValueUse(parent, use, self.obj)

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
builtins = lazy_lambda(lambda: mkModule('__builtins__', "__builtins__.py", False))
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
	
	return (val, atom)

def access_primitive(name, parent):
	(val, atom) = lookup_primitive(name)
	
	return (val, mkValueUse(parent, 0, atom))

# access: access a variable by name. abstracts over the difference between
# constdef/constuses and variables/valueuses.
# name is a string, parent is a trace node
# returns a pair of (value, trace of use)
def access(name, parent):
	#print "Access called"
	try:
		#print "access called on", (name, parent)
		(val, traceobj) = lookup(name)
		#print "access got", (val, traceobj), "from lookup"
	except NameError:
		#print "Access falling back to access_primitive"
		return access_primitive(name, parent)
	
	#print "access past try block"
	use = traceobj.makeAccess(parent, 0)
	#print "access returning", (val, use)
	return (val, use)

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

def exec_stmt(ast):
	assert isinstance(ast, _ast.stmt)

	if ast.__class__ == _ast.Expr:          # can't return
		res = eval_tracing(ast.value)
		res[0]()
	elif ast.__class__ == _ast.Assign:      # can't return
		exec_assign(ast)
	elif ast.__class__ == _ast.FunctionDef: # can't return
		exec_functiondef(ast)
	elif ast.__class__ == _ast.If: # the stmt, not the expr
		res = exec_if(ast)
		if res.__class__ == RetVal: # might return, but not necessarily
			return res
	elif ast.__class__ == _ast.Print:
		eval_print(ast)
	elif ast.__class__ == _ast.Return:
		return exec_return(ast)   # this one will definitely return :-)
	else:
		raise Exception, ("Unrecognized AST node %s!" % (ast.__class__.__name__,))
	
	return None

def eval_tracing(ast):
	assert isinstance(ast, _ast.expr)
	
	if ast.__class__ == _ast.BinOp:
		res = eval_binop(ast)
	elif ast.__class__ == _ast.BoolOp:
		res = eval_boolop(ast)
	elif ast.__class__ == _ast.Call:
		res = eval_call(ast)
	elif ast.__class__ == _ast.Name:
		res = eval_name(ast)
	elif ast.__class__ == _ast.Num:
		res = eval_num(ast)
	elif ast.__class__ == _ast.Str:
		res = eval_str(ast)
	elif ast.__class__ == _ast.UnaryOp:
		res = eval_unaryop(ast)
	else:
		raise Exception, ("Unrecognized AST node %s!" % (ast.__class__.__name__,))
	
	def wrapper():
		result = res[0]()
		print ast_indented_str(ast, 0), "\nEvaluates To:\n", result[0]
		return result
	
	return (wrapper, res[1])

def exec_assign(asn):
	assert asn.__class__ == _ast.Assign

	assert len(asn.targets) == 1
	name = asn.targets[0]
	assert name.__class__ == _ast.Name
	
	# ConstDef here basically puts the program into static single
	# assignment form. every assignment to a variable makes a new version,
	# and the symbol table always has the most recent one.

	trace = ConstDef(parents[-1],
	                 mkVariable(module, 0, 0, 0, 0, name.id, False))
		# make a new variable each time because the definition site
		# changes for each assignment to it.
	parents.append(trace.obj)
	entResult(trace.obj, 0)

	val = eval_tracing(asn.value)

	valr = val[0]()
#	for (name, cdef) in zip(asn.targets, traces):
#		entResult(cdef, 0)
#		assign(name.id, (valr[0], cdef))
#		resResult(cdef, val[1], 0) # val, not valr
	assign(name.id, (valr[0], trace))
	resResult(trace.obj, val[1], 0)
	parents.pop()
	
	return None

# binops are printed infix even if they're not marked that way because of lines
# 469-472 in <hat-src>/hattools/SExp.hs
primitive_add = lazy_writer("+", 2)
primitive_sub = lazy_writer("-", 2)
primitive_mul = lazy_writer("*", 2)
primitive_div = lazy_writer("//", 2) # only integers right now
def eval_binop(binop):
	assert binop.__class__ == _ast.BinOp
	
	left = eval_tracing(binop.left)
	right = eval_tracing(binop.right)
	
	if binop.op.__class__ == _ast.Add:
		app = mkApp2(parents[-1],
		             0,
		             mkValueUse(parents[-1], 0, primitive_add()),
		             left[1],
		             right[1])
		def ev():
			entResult(app, 0)
			leftr = left[0]()
			rightr = right[0]()
			res = (leftr[0] + rightr[0], mkInt(0, 0, leftr[0] + rightr[0]))
			resResult(app, res[1], 0)
			return res
	elif binop.op.__class__ == _ast.Sub:
		app = mkApp2(parents[-1],
		             0,
		             mkValueUse(parents[-1], 0, primitive_sub()),
		             left[1],
		             right[1])
		def ev():
			entResult(app, 0)
			leftr = left[0]()
			rightr = right[0]()
			res = (leftr[0] - rightr[0], mkInt(0, 0, leftr[0] - rightr[0]))
			resResult(app, res[1], 0)
			return res
	elif binop.op.__class__ == _ast.Mult:
		app = mkApp2(parents[-1],
		             0,
		             mkValueUse(parents[-1], 0, primitive_mul()),
		             left[1],
		             right[1])
		def ev():
			entResult(app, 0)
			leftr = left[0]()
			rightr = right[0]()
			res = (leftr[0] * rightr[0], mkInt(0, 0, leftr[0] * rightr[0]))
			resResult(app, res[1], 0)
			return res
	elif binop.op.__class__ == _ast.Div:
		app = mkApp2(parents[-1],
		             0,
		             mkValueUse(parents[-1], 0, primitive_div()),
		             left[1],
		             right[1])
		def ev():
			entResult(app, 0)
			leftr = left[0]()
			rightr = right[0]()
			res = (leftr[0] // rightr[0], mkInt(0, 0, leftr[0] // rightr[0]))
			resResult(app, res[1], 0)
			return res
	else:
		raise Exception, "Unrecognized BinOp!"
	
	return (ev, app)

primitive_and = lazy_writer("and", -1) # arity what?
primitive_or = lazy_writer("or", -1)
def eval_boolop(boolop):
	assert boolop.__class__ == _ast.BoolOp
	assert 2 <= len(boolop.values) <= 15 # might not even need the upper limit
	
	if boolop.op.__class__ == _ast.And:
		subs = map(lambda (x): eval_tracing(x), boolop.values)
		app = mkAppn(parents[-1],
		             0, 
		             mkValueUse(parents[-1], 0, primitive_and()),
		             len(boolop.values),
		             *tuple(map(lambda (x): x[1], subs)))
		def ev():
			entResult(app, 0)
			for this in subs:
				val = this[0]()
				if not val[0]:
					break
			resResult(app, this[1], 0)
			return val

		return (ev, app)
	
	elif boolop.op.__class__ == _ast.Or:
		subs = map(lambda (x): eval_tracing(x), boolop.values)
		app = mkAppn(parents[-1],
		             0, mkValueUse(parents[-1], 0, primitive_or()),
		             len(boolop.values),
		             *tuple(map(lambda (x): x[1], subs)))
		def ev():
			entResult(app, 0)
			for this in subs:
				val = this[0]()
				if val[0]:
					break
			resResult(app, this[1], 0)
			return val

		return (ev, app)
	
	else:
		raise Exception, "Unknown boolop!"

class traced_function(object):
	def __init__(self, args, body):
		self.args = args
		self.body = body

def trace_value(val, parent):
	if isinstance(val, int):
		return mkInt(parent, 0, val)
	else:
		raise Exception, ("Unhandled case in trace value: %s!" % (val,))

def eval_call(call):
	assert call.__class__ == _ast.Call

	# we don't handle all cases yet
	if (len(call.keywords) == 0
	    and call.starargs == None
	    and call.kwargs == None):
		func = eval_tracing(call.func)
		args = map(lambda(x):eval_tracing(x), call.args)
		
		funcr = func[0]()[0]
		argsr = map(lambda(x): x[0]()[0], args)
		
		if funcr.__class__ == traced_function:
			print "Evaluating a call to a traced function"
			
			app = mkAppn(parents[-1], 0, func[1], len(args), *tuple([x[1] for x in args]))
			# we already know that the function takes only
			# positional args, because exec_functiondef checked
			# that.
			frames.append(dict(zip([x.id for x in funcr.args.args],
			                       [(v, Param(r[1])) for (v, r) in zip(argsr, args)])))
			parents.append(app)
			
			print "New call frame:", frames[-1]
			
			try: # this stuff should really be in an exec_block function
				entResult(app, 0)
				res = exec_stmts(funcr.body)
				if isinstance(res, RetVal):
					resResult(app, res.val[1], 0)
					return (res.val[0], app) # right?
				else:
					resResult(app, mkValueUse(parents[-1], 0, primitive_none()), 0)
					return None # this is a statement. makes semantics interesting.
			finally:
				parents.pop()
				frames.pop()
				print "Done with call"
		elif callable(funcr): # calling an unwrapped function
			app = mkAppn(parents[-1], 0, func[1], len(args), *tuple(map(lambda(x):x[1], args)))
			def ev():
				parents.append(app)
				entResult(app, 0)
				innards = mkHidden(app)
				# NOTE: to make this work with untraced higher-order functions that call
				# traced closures, add a global variable "parent" and assign innards to it
				# right here. then make traced_functions callable, and make the behavior that
				# they interpret their code with the global parent variable.
				# you might then have to convert the data to a traced version right here,
				# which would suck, but it's the right way to do it (unless there's a way to
				# avoid the conversion, which would be wonderful, but probably not)
				# UNSOLVED PROBLEM: what if the traced closures return data to the untraced
				# function? how is it traced? probably by using subclasses
				#  - or alternatively, if you really do want to consider untraced functions
				#    black boxes, maybe it's reasonable to *not* trace it. this needs thought.
				entResult(innards, 0)
				val = funcr(*argsr)
				valt = trace_value(val, innards)
				resResult(innards, valt, 0)
				resResult(app, innards, 0)
				parents.pop()
				return (val, app)
			return (ev, app)
		else: # WOAH! why catch not-callables if we don't do anything about them?
			raise TypeError, ("Object " + func + " is not callable")
	else:
		raise Exception, "Unhandled case in eval_call!"

def exec_functiondef(fdef):
	assert fdef.__class__ == _ast.FunctionDef	

	# we don't handle all cases yet
	if (len(fdef.decorator_list) == 0
	    and len(fdef.args.defaults) == 0
	    and fdef.args.vararg == None
	    and fdef.args.kwarg == None):
	    	#print "exec_functiondef: running the if"
	    	assert all([isinstance(x, _ast.Name) and isinstance(x.ctx, _ast.Param)
	    	               for x in fdef.args.args]) # check my assumptions
		func = traced_function(fdef.args, fdef.body)
		trace = Variable(module,              # module
		                 0,                   # end
		                 0,                   # begin
		                 0,                   # fixity
		                 len(fdef.args.args), # arity
		                 fdef.name,           # name
		                 False)               # local
		assign(fdef.name, (func, trace))
	
		return None
	else:
		raise Exception, "Unhandled case in exec_functiondef!"

primitive_none = lazy_writer("None", 0)
def exec_if(exp):
	assert exp.__class__ == _ast.If
	
	cond = eval_tracing(exp.test)
	
	trace = mkIf(parents[-1], 0, cond[1])
	
	parents.append(trace)
	
	entResult(trace, 0)
	
	condr = cond[0]()
	
	if condr[0]:
		res = exec_stmts(exp.body)
	else:
		res = exec_stmts(exp.orelse)
	

	resResult(trace, mkValueUse(parents[-1], 0, primitive_none()), 0)
	
	parents.pop()
	
	return res

def eval_name(name):
	assert name.__class__ == _ast.Name
	
	# name: the only trace that doesn't compute a result?
	# no - literals don't either
	
	(val, trace) = access(name.id, parents[-1])
	def ev():
		return (val, trace)
	return (ev, trace)

def eval_num(num):
	assert num.__class__ == _ast.Num
	assert isinstance(num.n, int)
	
	trace = mkInt(parents[-1], 0, num.n)
	def ev():
		return (num.n, trace)
	return (ev, trace)

primitive_print = lazy_writer("print", -1)
primitive_stdout = lazy_writer("stdout", 0)
primitive_io = lazy_lambda(lambda: mkAbstract("IO"))
def eval_print(pr):
	assert pr.__class__ == _ast.Print
	assert 0 <= len(pr.values) <= 5
	
	if pr.dest != None:
		raise Exception("Printing to places other than sys.stdout not \
		                 implemented yet!")
	
	args = map(eval_tracing, pr.values)
	argsr = [x[0]()[0] for x in args]
	
	func = primitive_print()
	app = mkAppn(parents[-1], 0, mkValueUse(parents[-1], 0, func),
	               len(pr.values), *tuple([x[1] for x in args]))
		
	entResult(app, 0)
	hat_OutputTrace(app, " ".join([str(x) for x in argsr]))
	resResult(app, mkValueUse(app, 0, primitive_io()), 0)
	
	return None

def exec_return(ret):
	assert ret.__class__ == _ast.Return
	
	if ret.value:
		return RetVal(eval_tracing(ret.value))
	else:
		return RetVal((None,
		               mkValueUse(parents[-1], 0, primitive_none())))

def eval_str(ast):
	assert ast.__class__ == _ast.Str
	
	string = mkAbstract("\"%s\"" % ast.s)
	trace = mkValueUse(parents[-1], 0, string)
	def ev():
		return (ast.s, trace)
	return (ev, trace)

primitive_not = lazy_writer("not", 1)
primitive_true = lazy_writer("True", 0)   # looks like there's no mkBool, so...
primitive_false = lazy_writer("False", 0)
# note: True and False would probably be valueapps of constructors (or
# something) in "pure" Haskell. However, if this works, it's fine. And it might
# be a more accurate translation of Python anyway.
def eval_unaryop(unaryop):
	assert unaryop.__class__ == _ast.UnaryOp
	
	operand = eval_tracing(unaryop.operand)
	
	if unaryop.op.__class__ == _ast.Not:
		app = mkApp1(parents[-1],
		             0,
		             mkValueUse(parents[-1], 0, primitive_not()),
		             operand[1])
		def ev():
			entResult(app, 0)
			hid = mkHidden(app) # this represents the innards of 'not'
			entResult(hid, 0)
			operandr = operand[0]()
			if operandr[0]:
				res = (False, mkValueUse(hid, 0, primitive_false()))
			else:
				res = (True, mkValueUse(hid, 0, primitive_true()))
			resResult(hid, res[1], 0)
			resResult(app, hid, 0)
			return res
		return (ev, app)
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
	f = open(filename) # unsafe code here because I was making it work in Python 2.5
	mod = compile(f.read(), filename, 'exec', _ast.PyCF_ONLY_AST)
	f.close()
	return mod

# HAT-SPECIFIC WEIRDNESS: all programs have to appear to be in a module called
# 'Main', with a top-level variable called 'main' of arity 0 that does all the
# work.
def trace_file(filename):
	print "Tracing file ", filename
	
	mod = load_file(filename)

	print "Input AST:\n", ast_indented_str(mod, 0)
	
	assert mod.__class__ == _ast.Module

	# use everything but the last extension
	import os.path
	hat_Open("%s%s" % (os.path.split(filename)[0], # strange because I was making it work in Python 2.5
	                   os.path.splitext(os.path.split(filename)[1])[0]))
	
	global module
	module = mkModule('Main', filename, True)
	variable_main = mkVariable(module, 1, 3, 0, 0, "main", True)
	definition_main = mkConstDef(mkRoot(), variable_main)
	use_main = mkConstUse(0, 0, definition_main)
	
	parents.append(definition_main)
	
	# right now in the trace, the program was started and main was called
	# now, execution enters main
	entResult(definition_main, 0)
		
	print "Program Terminal:\n"
	try:
		# run the program in mod with parent definition_main
		exec_stmts(mod.body[:-1])
		if mod.body[-1].__class__ == _ast.Expr:
			res = eval_tracing(mod.body[len(mod.body)-1].value)
			res[0]() # experiment!
			resResult(definition_main, res[1], 0)
		else:
			exec_stmt(mod.body[-1])
			res = mkValueUse(definition_main, 0, primitive_io())
			resResult(definition_main, res, 0)
		parents.pop()
		assert len(parents) == 0
	finally:
		hat_Close()

def _main():
	import sys
	
	for filename in sys.argv[1:]:
		trace_file(filename)

if __name__ == '__main__':
	_main()
