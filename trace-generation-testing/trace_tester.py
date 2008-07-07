#!/usr/bin/python

from Trace import *

# is a use always a source position?

def init():
	# open test.hat, test.hat.output, and test.hat.bridge
	# and write a header to test.hat
	hat_Open('test')
	
	# the trace must start with a module called Main
	module_Main = mkModule('Main', 'test.py', True)

	# and the first item must be a variable called "main" of arity 0
	variable_main = mkVariable(module_Main, 1, 3, 0, 0, "main", True)
	
	# followed by the definition of "main"
	definition_main = mkConstDef(0, variable_main)
	
	# and a use of main
	use_main = mkConstUse(0, 0, definition_main)
	
	# up to this point is deduced from <hatdir>/src/hattools/detectutils.c,
	# in the function findMainUse
	
	# right now in the trace, the program was started and main was called
	
	# now, execution enters main
	entResult(definition_main, 0)
	
	# we produce a new integer value here.
	# mkInt: parent is the *definition* of main,
	#        use is 0 (for NoSrcPos),
	#        val is 42.
	val = mkInt(definition_main, 0, 42)
	
	# update main's result pointer with its value.
	# main is a constant applicative form, so its result is stored in its
	# definition (stupid Haskell-specific code).
	resResult(definition_main, val, 0)
	
	# and finish up by closing the file and flushing all the buffers
	hat_Close()

if __name__ == '__main__':
	init()

