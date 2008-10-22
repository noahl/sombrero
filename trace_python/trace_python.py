# trace Python programs

import _ast
import Tracer

# _traceObjects will be a top-level dictionary

class PythonTracer(object):
	def __new__(cls, exp):
		if isinstance(exp, str):
			exp = compile(exp, "traced_python_code", 'eval', _ast.PyCF_ONLY_AST)
		assert(isinstance(exp, _ast.AST))
		
		cls = _traceObjects(type(exp))
		
		return cls.__init__(exp)
	
	def __init__(self, *args):
		raise Exception("PythonTracer.__init__ called! args: " + args)

# all of the tracer objects have a writeTrace() method in addition to the step() method.
# this is necessary to trace lazily-evaluated forms like Python's if statement. We need
# to write the trace of the If before we start executing it so that errors will be
# attributed correctly. However, we can't write the trace of the if object until we have
# the traces of all of its subexpressions, and we can't evaluate them to get their traces,
# because we might get errors! So writeTrace() is used to write an object's trace without
# evaluating the object. writeTrace() returns a trace object. writeTrace() may be called
# more than once, but it will only write one trace.

# these methods, in effect, build the trace tree in memory. If we just kept these around,
# we could use them. However, that's supposed to be taken care of by the trace facility,
# so get rid of subnodes when step() is called.

# step() may only be called once for each tracer.

class BinOpTracer(PythonTracer):
	def __init__(self, exp): # exp is an _ast.BinOp
		self.op = exp.op
		self.left = PythonTracer(exp.left)
		self.right = PythonTracer(exp.right)
	
	def step(self):
		self.writeTrace() # self.tr has our trace now
		
		Tracer.enterComputation(self.tr)
		
		lres, ltr = self.left.step()
		rres, rtr = self.right.step()
		
		if isinstance(self.op, _ast.Add):
			res = lres + rres
		elif isinstance(self.op, _ast.Sub):
			res = lres - rres
		elif isinstance(self.op, _ast.Mult):
			res = lres * rres
		else: # if self.op isn't an _ast.Div, this is the least of our problems
			res = lres // rres # only integers right now
		
		tres = Tracer.makeLiteral(res)
		
		self.tr = Tracer.makeComputation(self.tr, tres)
		
		del self.op
		del self.left
		del self.right
		
		return (res, self.tr)
	
	def writeTrace(self):
		if hasattr(self, 'tr'):
			return self.tr
		
		left = self.left.writeTrace()
		right = self.right.writeTrace()
		
		if isinstance(self.op, _ast.Add):
			func = BinOpTracer.add()
		elif isinstance(self.op, _ast.Sub):
			func = BinOpTracer.sub()
		elif isinstance(self.op, _ast.Mult):
			func = BinOpTracer.mul()
		else:
			func = BinOpTracer.div()
		
		self.tr = Tracer.makeCombination(func, left, right)
		
		return self.tr

class IfTracer(PythonTracer):
	def __init__(self, exp):
		# exp is an _ast.If
		self.exp = exp
	
	def step(self):
		
