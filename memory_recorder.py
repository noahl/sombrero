class Literal(object):
	def __init__(self, parent, val):
		self.parent = parent
		parent.children.append(self)
		self.val = val
	
	# Program interface:
	
	def name():
		return str(self.val)
	
	def parent():
		return self.parent
	
	def children():
		return None
	
	def result():
		return None

class Function(object):
	def __init__(self, parent, name, argnames):
		self.parent = parent
		parent.children.append(self)
		self.name = name
		self.argnames = argnames
	
	# Data interface:
	
	def name():
		return self.name

class Computation(object):
	def __init__(self, parent, func, args):
		self.parent = parent
		parent.children.append(self)
		self.func = func
		self.args = args
		self.children = []
		self.entered = False
		self.result = None
	
	def enter(self):
		self.entered = True
	
	def finish(self, result):
		self.entered = False
		self.result = result
	
	# Program interface:
	
	def name(self):
		return "Running " + self.func.name()
	
	def parent():
		return self.parent
	
	def children():
		return self.children
	
	def result():
		return self.result

class TopLevel(object):
	def __init__(self):
		self.children = []

def makeLiteral(parent, val):
	return Literal(parent, val)

def makeFunction(parent, name, argnames):
	return Function(parent, name, argnames)

def makeComputation(parent, func, args):
	return Computation(parent, func, args)

def enterComputation(obj):
	obj.enter()

def finishComputation(obj, result):
	obj.finish(result)

