#!/usr/bin/python

# view.py: contains the parts of the user interface that need to know about
#          Program objects and such things. Connects to gui.py, which contains
#          the generic DAG-display code, and program.py, which actually knows
#          how to manipulate programs.

from program import Program, State
import gui

# for the canvas:
class ViewState(object):
	def __init__(self):
		self.programstate = State()
	
	def setgui(self, gui):
		self.gui = gui
	
	def context_choices(self):
		def makeNewProgramBox():
			b = ProgramBox(self.programstate.default_program(),
			               self)
			self.gui.addNode(b)

		return (("Make a new program box", makeNewProgramBox),
		        ("Import a new file",
		          lambda: gui.fileDialog(
		            lambda f: self.programstate.import_file(f))))

# a ProgramBox holds a computation. it may have a result
# a ProgramBox is the visual representation on the canvas of the same thing
#  that a Program represents in the application's abstract model.
# a ProgramBox can be a user object for Programs.
class ProgramBox(object):
	def __init__(self, program, viewstate):
		# the two main attributes are program and viewstate
		self.program = program
		self.viewstate = viewstate
		
	def setgui(self, gui):
		self.gui = gui
	
	def context_choices(self):
		return (("Show parent", self.show_parent),
		        ("Show children", self.show_children),
		        ("Show result", self.show_result))
	
	# name: temporary method to give the gui a representation string until
	#       we can get a real interface going.
	def name(self):
		return self.program.name()
	
	def recompute(self):
		print "Recompute!"
		#self.program()

	# program: returns self's program, but first makes sure it exists, and
	#          generates it if necessary
	# commented out until we generate programs from strings
	#def program(self):
		# TODO: save the old text box text, and only regenerate if the
		#       new text is different than the old.
	#	if not hasattr(self, "_program") or self._program is None:
	#		self._program = makeProgramFromString(
	#		    self.gui.text(),
	#		    self.programstate)
		
	#	return self._program
	
	def show_parent(self):
		if hasattr(self, "parent"):
			return # we're done in this case
		else:
			p = ProgramBox(self.program.parent(),
			               self.viewstate)
			self.parent = p
			self.gui.add_parent(p)
	
	def show_children(self):
		for c in self.program.children():
			self.gui.add_child(ProgramBox(c, self.viewstate))
	
	def show_result(self):
		self.gui.add_result(ProgramBox(self.program.result(),
		                               self.viewstate))

if __name__ == '__main__':
	gui.gui_go(ViewState())

# -------------
# ProgramBox <--> Program Interface:
#   The basic idea is that the Program should have all the knowledge of how it
# executes, and the ProgramBox should have all the knowledge of how it displays
# information as a graph. (Note: both of them share the underlying assumption
# that the program is, in fact, a graph.)
#
#   To make things more interesting, the ProgramBoxes need to know about order
# of evaluation. Specifically, there needs to be a notion of, "Program A caused
# program B to be executed," so that evaluation will display properly on the
# graph, and each program's subexpressions will be the things it *evaluated*.
#
#   Furthermore, there are only ProgramBoxes for *some* of the possible Program
# nodes, not all.
#
#   The current attempt to implement this idea is as follows. Because there are
# not ProgramBoxes for all Program nodes, the Programs need to have all of the
# information about links. Specifically, the Program needs to know what its
# parent is (and its call site?), what its children are, and what its result
# is. Therefore, Programs implement these three methods:
#
#   parent() :: Program - returns the parent of this program, or None
#   children() :: [Program] - returns the children of this program, as a list
#   result() :: Program - returns the result of this program, or None
#
#   In addition, the user interface will need enough information to display
# Programs nicely, so Programs implement this method too:
#
#   name() :: String - returns the name of the function this program represents
#
#   Finally (initially? :-)),  the user interface will want to be able to make
# new Programs given only a string and the overall program context, so there
# will be a function to do this:
#
#   makeProgram(expr, state) :: String -> State -> Program (makeProgramFromString)
# -------------

