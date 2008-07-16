#!/usr/bin/python

# gui.py: contains code for building a user interface in which the program
#         displays a tree to the user in a big canvas, which the user interacts
#         with through contextual menus.

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

# popupMenu: display a popup menu at the given coordinates (relative to the
#            root window) with the given menu. returns the same menu object,
#            which can be closed with its unpost() method
# usage: popupMenu(x, y, menu)
# TODO: This makes popups on top of *everything*. This is BAD!
def popupMenu(x, y, menu):
	# don't call popup.tk_popup(...) here, because it doesn't work right.
	menu.post(x, y)
	
	return menu

# makeMenu: take a master and a list of (string, function) pairs, and returns a
# Menu object with the strings as labels, the functions as matching commands,
# and no tearoff. The functions should take no arguments.
# usage: makeMenu(master, ("name", function), ("name2", function2), ...)
def makeMenu(master, *items):
	menu = Menu(master, tearoff = 0)
	
	for i in items:
		(lbl, call) = i
		popup.add_command(label = lbl, command = call)
	
	return menu


# TODO: I got the idea for an App class from the NMT Tkinter tutorial, but I
#       think it might be outdated or just wrong. I should check up on this and
#       then possibly change it.
class App(Frame):
	def __init__(self, backend, master=None):
		Frame.__init__(self, master, takefocus=0)
		
		self.backend = backend
		
		self.grid(sticky=N+S+E+W)
		self.columnconfigure(0, weight = 1)
		self.rowconfigure(0, weight = 1)
		
		top = self.winfo_toplevel()
		top.rowconfigure(0, weight = 1)
		top.columnconfigure(0, weight = 1)
		
		self.canvas = Viewer(backend, self)
		self.canvas.grid(row = 0,
		                 column = 0,
		                 sticky=N+E+S+W)

# TODO: why is viewer a separate class? This could all be part of App.
class Viewer(Canvas):
	def __init__(self, backend, master=None):
		Canvas.__init__(self, master, state = NORMAL, takefocus = 1,
		                background = "white")
		self.backend = backend
		# TODO: maybe None is a valid state? for some sort of pure viewer?
		self.bind("<Button-3>", self.handle_right_click, add="+")
		self.bind("<Button-1>", self.handle_left_click, add="+")
	
	# TODO: factor this and the ProgramBox's right click handler into one function
	def handle_right_click(self, event):
		# close our existing popup, if we have one
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup # this works without this line
		
		# then, get the context menu choices from the backend
		choices = backend.context_choices()
		if choices is not None and len(choices) > 0:
			self.popup = makeMenu(self, *choices)
			popupMenu(event.x_root, event.y_root, self.popup)
	
	def handle_left_click(self, event):
		self.focus_set()
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup # this works without this line.


# TODO: make a class ExpandingText, or ResizableText, and let people type into
#       it instead of a regular Text.

# a Node represents a node drawn in the canvas. There is a bijection between
# Node objects and squares drawn in the scrollarea.
class Node(object):
	def __init__(self, backend, canvas, x = 0, y = 0):
		self.canvas = canvas
		self.pos = (x, y)
		self.cmdfield = Text(canvas, background = "white",
		                     height = 1, # height is measured in lines
		                     width = 40, # width is measured in characters
		                     wrap = WORD # move a long word to a new line
		                    )
		
		self.window = canvas.create_window(x, y, window=self.cmdfield, anchor=NW)
		
		self.cmdfield.bind("<KeyPress-Return>", self.recompute, add="+")
		self.cmdfield.bind("<FocusOut>", self.recompute, add="+")
		
		# if we add this handler here, clicks on the border of the text field will call
		# this *and* the canvas' right-click handler, even if add is "".
		#self.canvas.tag_bind(self.window, "<Button-3>", self.handle_right_click, add="")
		
		# right clicks in the text field get passed to the text field's right-click
		# callback, not the canvas window's.
		self.cmdfield.bind("<Button-3>", self.handle_right_click, add="+")
		self.cmdfield.bind("<Button-1>", self.handle_left_click, add="+")
		
	# TODO: factor this and the Viewer's right click handler into one function.
	def handle_right_click(self, event):
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup
		
		choices = self.backend.context_choices()
		if choices is not None and len(choices) > 0:
			self.popup = popupMenu(event.x_root, event.y_root,
			                       makeMenu(self, *choices))
	
	def handle_left_click(self, event):
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup # this works without this line.

	def recompute(self, event):
		self.backend.recompute()
	
	# there are three types of connected nodes: parents, children, and results.
	
	# parents display above the child widget
	def add_parent(self, backend)
		(x, y) = self.pos
		if not hasattr(self, "parent") or self.parent is None:
			self.parent = Node(backend, self.canvas, x, y - 25)
	
	# children display below the parent widget
	def add_children(self, backends):
		for b in backends:
			self.add_child(b)
	
	def add_child(self, backend)
		(x, y) = self.pos
		
		if not hasattr(self, "children") or self.children is None:
			self.children = [Node(backend, self.canvas, x, y + 25)]
		else: # XXX: this doesn't actually work. also, we should draw connecting lines.
			self.children.append(Node(backend, self.canvas, x, y + 25))
	
	# results display to the right of the process node
	def add_result(self, backend):
		(x, y) = self.pos
		
		if not hasattr(self, "result") or self.result is None:
			self.result = Node(backend, self.canvas, x + 50, y)

def gui_go(backend):
	app = App(backend)
	app.master.title("Sombrero")
	return app.mainloop()
