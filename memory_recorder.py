class Value(object):
	def __init__(self, parent, val):
		self._parent = parent
		parent._children.append(self)
		self.val = val
	
	# Program interface:
	
	def name(self):
		return str(self.val)
	
	def parent(self):
		return self._parent
	
	def children(self):
		return [self._parent] # makes it work, but pretty odd
	
	def result(self):
		return None

class Function(object):
	def __init__(self, parent, name, argnames):
		self._parent = parent
		parent._children.append(self)
		self._name = name
		self.argnames = argnames
	
	# Data interface:
	
	def name(self):
		return self._name

class Reference(object):
	def __init__(self, parent, source, name, val):
		self._parent = parent
		parent._children.append(self)
		self._source = source
		self._name = name
		self.val = val
	
	# Program interface:
		
	def name(self):
		return self._name + " (" + str(self.val) + ")"
	
	def parent(self):
		return self._parent

	def children(self):
		return []

	def result(self):
		return None

	# And extra:

	def source(self):
		return self._source

class Computation(object):
	def __init__(self, parent, func, args):
		self._parent = parent
		parent._children.append(self)
		self.func = func
		self.args = args # args is a list
		self._children = []
		self.entered = False
		self._result = None
	
	def enter(self):
		self.entered = True
	
	def finish(self, result):
		self.entered = False
		self._result = result
	
	# Program interface:
	
	def name(self):
		return "Running " + self.func.name()
	
	def parent(self):
		return self._parent
	
	def children(self):
		return self._children + self.args # XXX: AAH! Args bad here!
	
	def result(self):
		return self._result

class Error(object):
	def __init__(self, parent, desc):
		self._parent = parent
		parent._children.append(self)
		self.desc = desc
	
	def name(self):
		return self.desc
	
	def parent(self):
		return self._parent
	
	def children(self):
		return []
	
	def result(self):
		return None

class TopLevel(object):
	def __init__(self):
		self._children = []
	def default_program(self):
		if hasattr(self, "dp"):
			return self.dp
		else:
			return None
top_level = TopLevel()

def makeValue(parent, val):
	v = Value(parent, val)
	
	#if not hasattr(top_level, "dp"):
	#	top_level.dp = v

	return v

def makeFunction(parent, name, argnames):
	f = Function(parent, name, argnames)
	
	#if not hasattr(top_level, "dp"):
	#	top_level.dp = f

	return f

def makeReference(parent, source, name, val):
	r = Reference(parent, source, name, val)

	return r

def makeComputation(parent, func, args):
	c = Computation(parent, func, args)
	
	#if not hasattr(top_level, "dp"):
	#	top_level.dp = c

	return c

def makeError(parent, desc):
	e = Error(parent, desc)
	
	return e

def enterComputation(obj):
	obj.enter()

def finishComputation(obj, result):
	obj.finish(result)

def default_program():
	return top_level.default_program()

def set_top_level_program(obj):
	top_level.dp = obj

# Tags
#   Tags are strings which may be attached to different trace objects, with the
#   condition that each tag is attached to only one object at a time. Therefore,
#   moving a tag to a new object is the same as removing it from its old one.
def makeTag(str):
	return Tag(str)
