class Literal(object):
	def __init__(self, val):
		self.val = val

class Function(object):
	def __init__(self, name, argnames):
		self.name = name
		self.argnames = argnames

class Computation(object):
	def __init__(self, func, args):
		self.func = func
		self.args = args
		self.entered = False
	
	def enter(self):
		self.entered = True
	
	def finish(self, result):
		self.entered = False
		self.result = result


def makeLiteral(val):
	return Literal(val)

def makeFunction(name, argnames):
	return Function(name, argnames)

def makeComputation(func, args):
	return Computation(func, args)

def enterComputation(obj):
	obj.enter()

def finishComputation(obj, result):
	obj.finish(result)
