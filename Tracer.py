# Tracer.py: general tracer stuff

# State: represent the state of the tracer. This should include open files and
#        global variables.

import trace_interpret

class State:
	def __init__(self):
		local_state = self
		self.openFile = None
		self.openFiles = []
	
	def open_file_pairs(self):
		return []

	def import_file(self, filename):
		if filename.endswith(".py"):
			f = PythonFile(filename)
		else:
			raise Exception("the file \"" + filename + "\" has an \
                                         unknown type, and cannot be imported.")
		
		f.open()

		return filename

local_state = False

# PythonFile: a type of file that might be open.

class PythonFile(object):
	def __init__(self, filename):
		self.filename = filename
		self.isOpen = False # "open" includes "resumed" here
        
        # These next four functions are not really necessary for a Python
        # file, but are great for a hat file (or any other on-disk format?)
	def open(self):
		if not self.isOpen:
			print "Opening Python file", self.filename
			trace_interpret.trace_file(self.filename)
			self.isOpen = True
	
	def suspend(self):
		if self.isOpen:
			self.isOpen = False
		# we close the hat file, but our functiondefs stay in the
		# environment
	
	def resume(self):
		if not self.isOpen:
			self.isOpen = True
	
	def close(self):
		if self.isOpen:
			self.isOpen = False
	
	def name(self):
		return self.filename

# programFromString: make a Program from the given string, with the given
#                    global state
def programFromString(string, state):
	# this function is actually not correctly implemented right now.
	# no matter what the string is, it will just return the offset of the
	# use of the function 'main' in the trace state.hatfile.
	return state.default_program()
