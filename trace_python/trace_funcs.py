#!/usr/bin/python

# trace_funcs.py: this file holds the actual functions that trace Python.
# They're here really because they're not interesting enough to clutter up the
# main file with.

import _ast
import Recorder
import sys

# the following statements are based on an unpleasant discovery I have recently
# made: Python import semantics are insane. Specifically, when you try to
# import '*' from a module, that means import all of the names currently
# defined in that module. This applies even if not all of the names in that
# module's source file have been created yet because that module is in the
# process of being loaded. I can understand why Python does this, but it means
# that the meaning of 'import *' in any given module depends on what other
# modules are importing this one, and whether that chain happens to lead back
# to the one you wanted to 'import *' from. To avoid this, I'm going to convert
# all of my variable references to use module names and never think about this
# again.

import trace_utils
import trace_interpret

primitive_assign = trace_utils.lazy_writer("=", 2)
primitive_none = trace_utils.lazy_lambda(lambda: Recorder.makeValue(Recorder.top_level, None))
def exec_assign(asn):
	assert asn.__class__ == _ast.Assign

	assert len(asn.targets) == 1
	name = asn.targets[0]
	assert name.__class__ == _ast.Name
	
	# First, we evaluate the assign's value

	trace = Recorder.makeComputation(trace_interpret.parents[-1], primitive_assign(), [])
	
	trace_interpret.parents.append(trace)
	Recorder.enterComputation(trace)

	val = trace_interpret.eval_tracing(asn.value)
	valr = val[0]()

	Recorder.finishComputation(trace, primitive_none())
	trace_interpret.parents.pop()

	# ConstDef here basically puts the program into static single
	# assignment form. every assignment to a variable makes a new version,
	# and the symbol table always has the most recent one.

	#trace = Accessible(trace_interpret.parents[-1],
	#		   Recorder.makeComputation(trace_interpret.parents[-1]))
		# make a new variable each time because the definition site
		# changes for each assignment to it.

	#trace_interpret.parents.append(trace.obj)

	#entResult(trace.obj, 0)

#	for (name, cdef) in zip(asn.targets, traces):
#		entResult(cdef, 0)
#		assign(name.id, (valr[0], cdef))
#		resResult(cdef, val[1], 0) # val, not valr
	trace_utils.assign(name.id, (valr[0], trace_utils.Accessible(trace_interpret.parents[-1],
								  trace)))

	#resResult(trace.obj, val[1], 0)

	#trace_interpret.parents.pop()
	
	return None

# binops are printed infix even if they're not marked that way because of lines
# 469-472 in <hat-src>/hattools/SExp.hs
primitive_add = trace_utils.lazy_writer("+", 2)
primitive_sub = trace_utils.lazy_writer("-", 2)
primitive_mul = trace_utils.lazy_writer("*", 2)
primitive_div = trace_utils.lazy_writer("//", 2) # only integers right now
def eval_binop(binop):
	assert binop.__class__ == _ast.BinOp
	
	left = trace_interpret.eval_tracing(binop.left)
	right = trace_interpret.eval_tracing(binop.right)
	
	if binop.op.__class__ == _ast.Add:
		trace_op = primitive_add()
		comb_func = lambda x,y: x + y
	elif binop.op.__class__ == _ast.Sub:
		trace_op = primitive_sub()
		comb_func = lambda x,y: x - y
	elif binop.op.__class__ == _ast.Mult:
		trace_op = primitive_mul()
		comb_func = lambda x,y: x * y
	elif binop.op.__class__ == _ast.Div:
		trace_op = primitive_div()
		comb_func = lambda x,y: x // y
	else:
		raise Exception, "Unrecognized BinOp!"
	
	app = trace_utils.mkAppn(trace_interpret.parents[-1],
	      			 0,
	      			 trace_op,
	      			 2,
	      			 left[1],
	      			 right[1])
	
	def ev():
		trace_interpret.parents.append(app)
		Recorder.enterComputation(app)		
		
		leftr = left[0]()[0]   # leftr and rightr:
		rightr = right[0]()[0] # the result values
		resval = comb_func(leftr, rightr)
		res = (resval, Recorder.makeValue(app, resval))
		
		Recorder.finishComputation(app, res[1])
		trace_interpret.parents.pop()
		
		return res
	
	return (ev, app)

primitive_and = trace_utils.lazy_writer("and", -1) # arity what?
primitive_or = trace_utils.lazy_writer("or", -1)
def eval_boolop(boolop):
	assert boolop.__class__ == _ast.BoolOp
	assert 2 <= len(boolop.values) <= 15 # might not even need the upper limit
	
	if boolop.op.__class__ == _ast.And:
		trace_op  = primitive_and()
		interrupt_test = lambda (x): not x
	elif boolop.op.__class__ == _ast.Or:
		trace_op = primitive_or()
		interrupt_test = lambda (x): x
	else:
		raise Exception, "Unknown boolop!"
	
	subs = map(lambda (x): trace_interpret.eval_tracing(x), boolop.values)
	app = trace_utils.mkAppn(trace_interpret.parents[-1],
	             0,
	             trace_op,
	             len(boolop.values),
	             *tuple(map(lambda (x): x[1], subs)))
	def ev():
		trace_interpret.parents.append(app)
		Recorder.enterComputation(app)
		for this in subs:
			val = this[0]()
			if interrupt_test(val[0]):
				break
		Recorder.finishComputation(app, this[1])
		trace_interpret.parents.pop()
		return val
		
	return (ev, app)

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
		func = trace_interpret.eval_tracing(call.func)
		args = map(lambda(x):trace_interpret.eval_tracing(x), call.args)
		
		funcr = func[0]()[0]
		argsr = map(lambda(x): x[0]()[0], args)
		
		if funcr.__class__ == trace_utils.traced_function:
			#print "Evaluating a call to a traced function"
			
			app = mkAppn(trace_interpret.parents[-1], 0, func[1], len(args), *tuple([x[1] for x in args]))
			# we already know that the function takes only
			# positional args, because exec_functiondef checked
			# that.
			frames.append(dict(zip([x.id for x in funcr.args.args],
			                       [(v, Param(r[1])) for (v, r) in zip(argsr, args)])))
			trace_interpret.parents.append(app)
			
			#print "New call frame:", frames[-1]
			
			try: # this stuff should really be in an exec_block function
				entResult(app, 0)
				res = exec_stmts(funcr.body)
				if isinstance(res, RetVal):
					resResult(app, res.val[1], 0)
					return (res.val[0], app) # right?
				else:
					resResult(app, mkValueUse(trace_interpret.parents[-1], 0, primitive_none()), 0)
					return None # this is a statement. makes semantics interesting.
			finally:
				trace_interpret.parents.pop()
				frames.pop()
				#print "Done with call"
		elif callable(funcr): # calling an unwrapped function
			app = mkAppn(trace_interpret.parents[-1], 0, func[1], len(args), *tuple(map(lambda(x):x[1], args)))
			def ev():
				trace_interpret.parents.append(app)
				entResult(app, 0)
				innards = mkHidden(app)
				# NOTE: to make this work with untraced higher-order functions that call
				# traced closures, add a global variable "parent" and assign innards to it
				# right here. then make trace_utils.traced_functions callable, and make the behavior that
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
				trace_interpret.parents.pop()
				return (val, app)
			return (ev, app)
		else: # WOAH! why catch not-callables if we don't do anything about them?
			raise TypeError, ("Object " + func + " is not callable")
	else:
		raise Exception, "Unhandled case in eval_call!"

primitive_eq = trace_utils.lazy_writer("==", 2)
primitive_neq = trace_utils.lazy_writer("!=", 2)
primitive_lt = trace_utils.lazy_writer("<", 2)
primitive_gt = trace_utils.lazy_writer(">", 2)
primitive_lte = trace_utils.lazy_writer("<=", 2)
primitive_gte = trace_utils.lazy_writer(">=", 2)
primitive_is = trace_utils.lazy_writer("is", 2)
primitive_isnt = trace_utils.lazy_writer("is not", 2)
primitive_in = trace_utils.lazy_writer("in", 2)
primitive_nin = trace_utils.lazy_writer("not in", 2)
cmpoptable = {_ast.Eq    : (primitive_eq, lambda a,b: a == b),
              _ast.NotEq : (primitive_neq, lambda a,b: a != b),
              _ast.Lt    : (primitive_lt, lambda a,b: a < b),
              _ast.LtE   : (primitive_lte, lambda a,b: a <= b),
              _ast.Gt    : (primitive_gt, lambda a,b: a > b),
              _ast.GtE   : (primitive_gte, lambda a,b: a >= b),
              _ast.Is    : (primitive_is, lambda a,b: a is b),
              _ast.IsNot : (primitive_isnt, lambda a,b: a is not b),
              _ast.In    : (primitive_in, lambda a,b: a in b),
              _ast.NotIn : (primitive_nin, lambda a,b: a not in b)}
def eval_compare(compare):
	assert compare.__class__ == _ast.Compare
		
	lt = trace_interpret.eval_tracing(compare.left)
	rt = trace_interpret.eval_tracing(compare.comparators[0])
	oper = cmpoptable[compare.ops[0].__class__]
	ap = mkApp2(trace_interpret.parents[-1],
	             0,
	             mkValueUse(trace_interpret.parents[-1], 0, oper[0]()),
	             lt[1],
	             rt[1])
	
	def ev():
		left = lt  # next four lines are because Python doesn't
		right = rt # actually do lexical scoping
		app = ap
		op = oper
		leftr = left[0]()[0]
		rightr = right[0]()[0]
		entResult(app, 0)
		pyres = op[1](leftr, rightr) # Python result - doesn't have a trace
		
		if not pyres:
			tres = mkValueUse(app, 0, primitive_false())
			resResult(app, tres, 0)
			return (False, tres)
		
		left = right
		
		# we chain traced comparisons so that each non-final one
		# results in the next. (TODO: reconsider this? I can't tell if
		# it's elegant or a terrible hack.)
		for (op, val) in zip(compare.ops[1:], compare.comparators[1:]):
			opt = cmpoptable[op.__class__]
			right = trace_interpret.eval_tracing(val)
			napp = mkApp2(trace_interpret.parents[-1],
			              0,
			              mkValueUse(trace_interpret.parents[-1], 0, opt[0]()),
			              left[1],
			              right[1])
			resResult(app, napp, 0)
			entResult(napp, 0)
			leftr = left[0]()[0]
			rightr = right[0]()[0]
			pyres = opt[1](leftr, rightr)
			if not pyres:
				tres = mkValueUse(napp, 0, primitive_false())
				resResult(napp, tres, 0)
				return (False, tres)
			left = right
			app = napp
		
		tres = mkValueUse(app, 0, primitive_true())
		resResult(app, tres, 0)
		return (True, tres)
	
	return (ev, ap)

def exec_functiondef(fdef):
	assert fdef.__class__ == _ast.FunctionDef	

	# we don't handle all cases yet
	if (len(fdef.decorators) == 0
	    and len(fdef.args.defaults) == 0
	    and fdef.args.vararg == None
	    and fdef.args.kwarg == None):
	    	#print "exec_functiondef: running the if"
	    	assert all([isinstance(x, _ast.Name) and isinstance(x.ctx, _ast.Param)
	    	               for x in fdef.args.args]) # check my assumptions
		func = trace_utils.traced_function(fdef.args, fdef.body)
		trace = Variable(module,              # module
		                 0,                   # end
		                 0,                   # begin
		                 3,                   # fixity (see artutils.h, line 78)
		                 len(fdef.args.args), # arity
		                 fdef.name,           # name
		                 False)               # local
		assign(fdef.name, (func, trace))
	
		return None
	else:
		raise Exception, "Unhandled case in exec_functiondef!"

primitive_none = trace_utils.lazy_writer("None", 0)
def exec_if(exp):
	assert exp.__class__ == _ast.If
	
	cond = trace_interpret.eval_tracing(exp.test)
	
	trace = mkIf(trace_interpret.parents[-1], 0, cond[1])
	
	trace_interpret.parents.append(trace)
	
	entResult(trace, 0)
	
	condr = cond[0]()
	
	if condr[0]:
		res = exec_stmts(exp.body)
	else:
		res = exec_stmts(exp.orelse)
	
	resResult(trace, mkValueUse(trace_interpret.parents[-1], 0, primitive_none()), 0)
	
	trace_interpret.parents.pop()
	
	return res

def eval_name(name):
	assert name.__class__ == _ast.Name
	
	# name: the only trace that doesn't compute a result?
	# no - literals don't either
	
	(val, trace) = trace_utils.access(name.id, trace_interpret.parents[-1])
	def ev():
		return (val, trace)
	return (ev, trace)

def eval_num(num):
	assert num.__class__ == _ast.Num
	assert isinstance(num.n, int)
	
	trace = Recorder.makeValue(trace_interpret.parents[-1], num.n)
	def ev():
		return (num.n, trace)
	return (ev, trace)

primitive_print = trace_utils.lazy_writer("print", -1)
primitive_stdout = trace_utils.lazy_writer("stdout", 0)
primitive_io = trace_utils.lazy_lambda(lambda: mkAbstract("IO"))
def eval_print(pr):
	assert pr.__class__ == _ast.Print
	assert 0 <= len(pr.values) <= 5
	
	if pr.dest != None:
		raise Exception("Printing to places other than sys.stdout not \
		                 implemented yet!")
	
	args = map(trace_interpret.eval_tracing, pr.values)
	argsr = [x[0]()[0] for x in args]
	
	func = primitive_print()
	app = mkAppn(trace_interpret.parents[-1], 0, mkValueUse(trace_interpret.parents[-1], 0, func),
	               len(pr.values), *tuple([x[1] for x in args]))
		
	entResult(app, 0)
	hat_OutputTrace(app, " ".join([str(x) for x in argsr]))
	resResult(app, mkValueUse(app, 0, primitive_io()), 0)
	
	return None

def exec_return(ret):
	assert ret.__class__ == _ast.Return
	
	if ret.value:
		return RetVal(trace_interpret.eval_tracing(ret.value))
	else:
		return RetVal((None,
		               mkValueUse(trace_interpret.parents[-1], 0, primitive_none())))

def eval_str(ast):
	assert ast.__class__ == _ast.Str
	
	trace = Recorder.makeValue(trace_interpret.parents[-1], ast.s)
	def ev():
		return (ast.s, trace)
	return (ev, trace)

primitive_not = trace_utils.lazy_writer("not", 1)
primitive_true = trace_utils.lazy_writer("True", 0)   # looks like there's no mkBool, so...
primitive_false = trace_utils.lazy_writer("False", 0)
# note: True and False would probably be valueapps of constructors (or
# something) in "pure" Haskell. However, if this works, it's fine. And it might
# be a more accurate translation of Python anyway.
def eval_unaryop(unaryop):
	assert unaryop.__class__ == _ast.UnaryOp
	
	operand = trace_interpret.eval_tracing(unaryop.operand)
	
	if unaryop.op.__class__ == _ast.Not:
		app = mkApp1(trace_interpret.parents[-1],
		             0,
		             mkValueUse(trace_interpret.parents[-1], 0, primitive_not()),
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
