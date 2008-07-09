#!/usr/bin/python

from Tkinter import *

# fileDialog: let the user type in a file pathname, and give it to the procedure target
def fileDialog(target):
	def accept():
		text = entry.get()
		dialog.destroy()
		target(text)
	
	dialog = Toplevel() # one row, two columns
	
	dialog.columnconfigure(1, weight = 1)
	
	label = Label(dialog, text="Enter the path to a file:")
	label.grid(row=0, column=0, sticky=N+S+E+W)
	
	entry = Entry(dialog)
	entry.grid(row=0, column=1, sticky=N+S+E+W)
	
	button = Button(dialog, text = "Import", command = accept)
	button.grid(row=0, column=2, sticky=N+S+E+W)

class App(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master, takefocus=0)
		
		self.grid(sticky=N+S+E+W)
		self.columnconfigure(0, weight = 1)
		self.rowconfigure(0, weight = 1)
		
		top = self.winfo_toplevel()
		top.rowconfigure(0, weight = 1)
		top.columnconfigure(0, weight = 1)
		
		self.state = State()
		
		self.canvas = Viewer(self.state, self)
		self.canvas.grid(row = 0,
		                 column = 0,
		                 sticky=N+E+S+W)

# TODO: why is viewer a separate class? This could all be part of App.
class Viewer(Canvas):
	def __init__(self, state, master=None):
		Canvas.__init__(self, master, state = NORMAL, takefocus = 1,
		                background = "white")
		self.state = state
		# TODO: maybe None is a valid state? for some sort of pure viewer?
		self.bind("<Button-3>", self.handle_right_click, add="+")
		self.bind("<Button-1>", self.handle_left_click, add="+")
	
	def handle_right_click(self, event):
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
		# TODO: This makes popups on top of *everything*. This is BAD!
		popup = Menu(self, tearoff=0)
		popup.add_command(label = "Make new program box",
		                  command = lambda: ProgramBox(self, state, x = event.x, y = event.y))
		popup.add_command(label = "Import a new file",
		                  command = lambda: fileDialog(lambda f: self.state.import_file(f)))
		self.popup = popup
		popup.post(event.x_root, event.y_root)
	
	def handle_left_click(self, event):
		self.focus_set()
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()


# TODO: make a class ExpandingText, or ResizableText, and let people type their
#       programs into it instead of a regular Text.

# a ProgramBox holds a computation. it may have a result
# a ProgramBox is *visual representation on the canvas* of the same thing that
#  a Program represents in the application's abstract model.
# a ProgramBox can be a user object for Programs.
class ProgramBox(object):
	def __init__(self, state, canvas, x = 0, y = 0):
		self.state = state
		self.canvas = canvas
		self.cmdfield = Text(canvas, background = "white",
		                     height = 1, # height is measured in lines
		                     width = 40, # width is measured in characters
		                     wrap = WORD # move a long word to a new line
		                    )
		self.window = canvas.create_window(x, y, window=self.cmdfield, anchor=NW)
		
		self.cmdfield.bind("<KeyPress-Return>", self.recompute, add="+")
		self.cmdfield.bind("<FocusOut>", self.recompute, add="+")
	
	def recompute(self, event):
		print "Recompute!"
	
	# methods for the Program to call:
	
	# makeResult: called by the program object when it replaces itself with
	#             a different, equivalent Program.
	# TODO: should this be called makeContinuation instead?
	def makeResult(self, result)
		# result is a Program object
		# return a Program just like result, but suitable for execution
		# (i.e., a Program just like result, but has a user object)
	
	# makeSubprogram: called by the program object when it spawns another
	#                 Program to do some work
	def makeSubprogram(self, sub)
		# sub is a Program object or a Value object
		# return a Program just like sub, but with a user object (so it
		# can be used in a traced computation, for instance)

# -------------
# ProgramBox - Program Interface:
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
#   The current attempt to implement this idea is as follows. Think of two
# separate types of objects, Programs and ProgramKernels. A ProgramKernel is
# something that can make a Program (a "thunk", even :-) ). Each Program knows
# its runtime object, which is something it can call to do two things:
#
#   - spawn a subprogram (with makeSubprogram)
#   - result in a value (with makeResult)
#
#   makeResult takes either a Value object, if the program results in a value,
# or a ProgramKernel object, if it results in another program. makeResult
# returns either the Value object or the Program object created from the
# ProgramKernel.
#   makeSubprogram takes a ProgramKernel. it returns a new Program object
# representing the subcomputation, which
# makeSubprogram returns a new Program object, which the calling program can
# use to help it solve the subproblem.
#
#   Open question: if a program calls makeSubprogram, and then asks the
# resulting program to evaluate itself again, and maybe so on a few more times,
# how does all of this get attributed to the right program? and who knows what
# a program's parent is, and how do they express that information? and are
# these the same question? (well, a solution to the second would solve the
# first one too.)

# Program: dummy class so I can think about things
class Program(object):
	def __init__(self, kernel, runtime):
		self.kernel = kernel
		self.runtime = runtime
	
	# evaluate: run this program.
	def evaluate(self):
		...
	
	def result(self):
		# return a program object
	
	def children(self):
		# return a list of program objects

def makeProgramFromString(string, state):
	Make a program object from the string in the given state

# class State: holds the state of a computer. Provides the environment for
# executing programs.
class State(object):
	def import_file(self, filename):
		print "Importing file", repr(filename), "!"

app = App()
app.master.title("Sombrero")
app.mainloop()
