#!/usr/bin/python

# Not using the compiler module because it's depreciated, and will be gone in
# Python 3.0. This is kind of too bad, but not a complete tragedy, since the
# module was badly documented, and didn't do what its documentation said it did
# anyway. Hopefully _ast will be a better solution.

import _ast

# tracing_ast: given the AST of a program, return the AST of another program
# that generates a trace for the first one.

# note: tracing_ast is presently implemented as a giant dispatch. this is okay,
# but there is also another, perhaps slightly more elegant, and perhaps more
# flexible way to do it. I could just add the conversions to the classes,
# giving each of them the same name, and let the method calling machinery
# handle the dispatch. this might be somewhat more elegant, and it might also
# be more flexible, since each class' method could take different arguments, as
# long as its callers all used it appropriately (which they could, because they
# know the class of all of their fields because the classes come from the
# grammar. of course you could only specialize the classes that match the left-
# hand sides of grammar rules, not the right-hand sides, but this would be
# fine)

def tracing_ast(ast):
	if ast.__class__ == _ast.Module:
		return traced_module(ast)
	elif ast.__class__ == _ast.Assign:
		return traced_assign(ast)
	elif ast.__class__ == _ast.Name:
		return traced_name(ast)
	elif ast.__class__ == _ast.Num:
		return traced_num(ast)
	else:
		raise Exception, "Unrecognized AST!"

def traced_module(module):
	assert module.__class__ == _ast.Module # should these assertions use isinstance()?

	# a traced module looks like:
	
	# import Trace
	# _module = mkModule(...)  <-- this is pretty hackish.
	# <body>
	
	# computing pre like this feels fragile and hard to change, and it not
	# a general solution. however, building it programmatically is really,
	# really hard
	pre = compile("import Trace; _module = mkModule(\"%s\", \"%s\", True)" % (modname, filename),
	              filename, 'exec', _ast.PyCF_ONLY_AST)
	
	assert pre.__class__ == _ast.Module

	mod = _ast.Module()
	
	mod.body = pre.body + map(tracing_ast, module.body)
	
	return mod

def traced_assign(assign):
	assert assign.__class__ == _ast.Assign
	
	
	
	return assign

def traced_name(name):
	assert name.__class__ == _ast.Name
	
	return name

def traced_num(num):
	assert num.__class__ == _ast.Num
	
	return num

# ast_str: pretty hackish. will go into an infinite loop if the ast contains
# cycles
def ast_str(ast):
	if isinstance(ast, _ast.AST): # all ASTs have a _fields attribute
		if ast._fields != None:
			subs = tuple(ast_str(ast.__dict__[x]) for x in ast._fields)
			return ast.__class__.__name__ + "(" + " ".join(subs) + ")"
		else:
			return ast.__class__.__name__
	elif isinstance(ast, list): # some attributes are lists of ASTS
		return "[" + " ".join(map(ast_str, ast)) + "]"
	elif ast == None: # some optional attributes are None
		return "None"
	else:
		return str(ast)

# ast_indented_str: still hackish and still loops, but gives nicer output now.
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

def load_test():
	# H * A * C * K
	import os
	os.chdir('testing')

	global modname
	global filename

	modname = 'Main'
	filename = 'test.py'
	
	return compile(open(filename).read(), filename, 'exec', _ast.PyCF_ONLY_AST)

def file_name_base(path): # do I really want this? maybe only the first extension *should* come off
	import os.path
	
	root, ext = os.path.splitext(os.path.basename(path))
	
	while ext != '':
		root, ext = os.path.splitext(root)
	
	return root

# HAT-SPECIFIC WEIRDNESS: this program will only produce correct Hat traces if
# the Python file you're tracing happens to define a variable called main which
# does all of the work. This will be fixed before this tracer is considered
# ready for use.
# proposed solution: make a special traced_main_module() function that wraps its
# body in a function called main() and makes everything look nice for hat. Or,
# fix Hat.
if __name__ == '__main__':
	mod = load_test()

	print "Input AST:\n", ast_indented_str(mod, 0)
	
	mod = tracing_ast(mod)
	
	print "Output AST:\n", ast_indented_str(mod, 0)
	
	import os.path
	from Trace import *
	
	hat_Open(file_name_base(filename))
	
	print "Program Terminal:\n"
	try:
		exec(compile(mod, filename, 'exec'))
	finally:
		hat_Close()

