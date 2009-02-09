#!/usr/bin/python

# view.py: contains the parts of the user interface that need to know about
#          Program objects and such things. Connects to gui.py, which contains
#          the generic DAG-display code, and program.py, which actually knows
#          how to manipulate programs.

from Tracer import State, programFromString
import gui
import Recorder
import sys

# for the canvas:
class ViewState(object):
	def __init__(self, programstate, filestate):
		self.programstate = programstate
		self.filestate = filestate
	
	def setgui(self, gui):
		self.gui = gui
	
	def makeNewProgramBox(self, program):
		b = ProgramBox(program, self)
		self.gui.addNode(b)
	
	def makeDefaultProgramBox(self):
		self.makeNewProgramBox(Recorder.default_program())
	
	def makeEntryBox(self):
		self.gui.addEntryNode(EntryBox(self))
	
	def context_choices(self):
		return (("Enter a program", self.makeEntryBox),
		        ("Make a new program box", self.makeDefaultProgramBox),
		        ("Import a new file",
		          lambda: gui.fileDialog(
		            lambda f: self.programstate.import_file(f))))

# an EntryBox holds a string, which will be interpreted as a Python expression.
class EntryBox(object):
	def __init__(self, viewstate):
		self.viewstate = viewstate
		self.text = None
	
	def setgui(self, gui):
		self.gui = gui
	
	def context_choices(self):
		return ()
	
	def recompute(self):
		text = self.gui.text()
		if not text == self.text:
			self.text = text
			pr = programFromString(text, self.viewstate.programstate)
			self.gui.add_result(ProgramBox(pr, self.viewstate))

# a ProgramBox holds a computation. it may have a result.
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
		        ("Show result", self.show_result),
		        (),
		        ("Hide this", self.hide))
	
	# name: temporary method to give the gui a representation string until
	#       we can get a real interface going.
	def name(self):
		print "Getting name of program", self.program
		return self.program.name()
	
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
		r = self.program.result()
		
		if r is not None:
			self.gui.add_result(ProgramBox(r, self.viewstate))
	
	def hide(self):
		self.gui.delete()
	
	def __str__(self):
		return self.program.__str__()
	__repr__ = __str__

class FileState(object):
	def __init__(self, programstate):
		self.programstate = programstate
		# also have self.viewstate, thanks to a hack.
	
	def default_text(self):
		return "Choose a file"
	
	def context_choices(self):
		filepairs = self.programstate.open_file_pairs()
		choices = [(fname, lambda: self.programstate.switch_to_file(f))
		           for (fname, f) in filepairs]
		if len(choices) > 0:
			choices.append(())
		choices.append(("Choose a file", self.import_file))
		return tuple(choices)
	
	def import_file(self):
		gui.fileDialog(lambda f: self.programstate.import_file(f))
	
	def go(self):
		self.viewstate.makeDefaultProgramBox()

if __name__ == '__main__':
	ps = State()
	fs = FileState(ps)
	vs = ViewState(ps, fs)
	fs.viewstate = vs # XXX: hack.
	
	# read files to import from the command line
	for f in sys.argv[1:]:
		ps.import_file(f)
	
	gui.gui_go(vs, fs)

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

