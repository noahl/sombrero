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

def makeProgramFromString(string, state):
	Make a program object from the string in the given state

# Program: dummy class so I can think about things
class Program(object):
	def __init__(self, user_object):
		self.user = user_object

# class State: holds the state of a computer. Provides the environment for
# executing programs.
class State(object):
	def import_file(self, filename):
		print "Importing file", repr(filename), "!"

app = App()
app.master.title("Sombrero")
app.mainloop()
