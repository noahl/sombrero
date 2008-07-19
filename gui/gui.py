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
	
	# idea: for real popup menus, post the menu, then set the grab so all
	# events go to the menu. when the menu gets a click, if the click is
	# outside the menu's area, it can ungrab events, unpost itself, and
	# resend the event.
	
	return menu

# makeMenu: take a master and a list of (string, function) pairs, and returns a
# Menu object with the strings as labels, the functions as matching commands,
# and no tearoff. The functions should take no arguments.
# usage: makeMenu(master, ("name", function), ("name2", function2), ...)
def makeMenu(master, *items):
	menu = Menu(master, tearoff = 0)
	
	for i in items:
		(lbl, call) = i
		menu.add_command(label = lbl, command = call)
	
	return menu


# TODO: I got the idea for an App class from the NMT Tkinter tutorial, but I
#       think it might be outdated or just wrong. I should check up on this and
#       then possibly change it.
# Note: the App is not a real gui class. It doesn't register itself with its
# backend, because it doesn't have any clear purpose in the program. It should
# probably go away.
class App(Frame):
	def __init__(self, backend, master=None):
		Frame.__init__(self, master, takefocus=0)
		
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
		if hasattr(backend, "setgui"):
			backend.setgui(self)
		# TODO: maybe None is a valid state? for some sort of pure viewer?
		self.bind("<Button-3>", self.handle_right_click, add="+")
		self.bind("<Button-1>", self.handle_left_click, add="+")
	
	def addNode(self, backend):
		if hasattr(self, "popup_loc") and self.popup_loc is not None:
			(x, y) = self.popup_loc
		else:
			(x, y) = (50, 50)
		
		n = Node(backend, self, x = x, y = y)
	
	# TODO: factor this and the ProgramBox's right click handler into one function
	def handle_right_click(self, event):
		# close our existing popup, if we have one
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup # this works without this line
			del self.popup_loc
		
		# then, get the context menu choices from the backend
		choices = self.backend.context_choices()
		if choices is not None and len(choices) > 0:
			self.popup = makeMenu(self, *choices)
			self.popup_loc = (event.x, event.y)
			popupMenu(event.x_root, event.y_root, self.popup)
	
	def handle_left_click(self, event):
		self.focus_set()
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup # this works without this line.


# TODO: make a class ExpandingText, or ResizableText, and let people type into
#       it instead of a regular Text.

# idea: factor this into a ProgramText class, which interfaces with the
# ProgramBox and responds to events, and a Node class, which only deals with
# making windows in the canvas and making new nodes.

# a Node represents a node drawn in the canvas. There is a bijection between
# Node objects and squares drawn in the scrollarea.
class Node(object):
	def __init__(self, backend, canvas, x = 0, y = 0):
		self.canvas = canvas
		self.textfield = ProgramText(backend, canvas, self)
		
		self.window = canvas.create_window(x, y, window=self.textfield, anchor=NW)
				
		# if we add this handler here, clicks on the border of the text field will call
		# this *and* the canvas' right-click handler, even if add is "".
		#self.canvas.tag_bind(self.window, "<Button-3>", self.handle_right_click, add="")
		
		# right clicks in the text field get passed to the text field's right-click
		# callback, not the canvas window's, so don't bind them here.
	
	
	# there are three types of connected nodes: parents, children, and results.
	
	# in order to make everything work correctly, each Node needs to
	# know about its parent, child, and result Nodes if they are
	# displayed, so that the entire tree can shift together. however,
	# finding the boxes we need to move to make space should be done with
	# the canvas' find_... methods, so that we don't assume that we're the
	# only tree around.

	# add_offset_node: add a new node at a given offset from this one.
	def add_offset_node(self, backend, dx, dy):
		(x1, y1, x2, y2) = self.canvas.bbox(self.window)
		
		if dx > 0: # there's also a special python ifExp form. use it?
			x = x2 + dx
		else:
			x = x1 + dx
		
		if dy > 0:
			y = y2 + dy
		else:
			y = y1 + dy
		
		Node(backend, self.canvas, x, y)

# ProgramText: a type of Text object to handle the actual display of a program.
# TODO: this class was broken off of Node, and I am not at all sure that it
# should have been. Consider this, and figure out if one is right.
class ProgramText(Text):
	def __init__(self, backend, canvas, node):
		self.backend = backend
		if hasattr(backend, "setgui"):
			backend.setgui(self)
		self.node = node
		self.canvas = canvas
		text = self.backend.name()
		Text.__init__(self, canvas, background = "white",
		              height = 1, # height is measured in lines
		              width = len(text), # width is measured in characters
		              wrap = WORD # move a long word to a new line
		             )
		self.insert("1.0", text)
		self.config(state = DISABLED)

		self.bind("<Button-3>", self.handle_right_click, add="+")
		self.bind("<Button-1>", self.handle_left_click, add="+")
	
	# Event handling functions:
	
	# TODO: factor this and the Viewer's right click handler into one function.
	def handle_right_click(self, event):
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup
		
		choices = self.backend.context_choices()
		if choices is not None and len(choices) > 0:
			self.popup = popupMenu(event.x_root, event.y_root,
			                       makeMenu(self.canvas, *choices))
	
	def handle_left_click(self, event):
		if hasattr(self, "popup") and self.popup is not None:
			self.popup.unpost()
			del self.popup # this works without this line.
	
	# Interface functions for the backend:
	
	# TODO: take this function out and replace it with a real interface.
	def text(self):
		return self.get("1.0", "end")
		# "end" works, "END" does not. Is Tkinter documented at all?
		# Evidence suggests not.
	
	def add_parent(self, backend):
		self.node.add_offset_node(backend, 0, -25)
	
	def add_child(self, backend):
		self.node.add_offset_node(backend, 0, 25)
	
	def add_result(self, backend):
		self.node.add_offset_node(backend, 25, 0)


def gui_go(backend):
	app = App(backend)
	app.master.title("Sombrero")
	return app.mainloop()

# GUI <--> Backend Interface
# Each gui object takes a backend as the first argument of its constructor. The
# backend object has all the model-specific intelligence for the object.
#
# If the backend object has a method setgui, it will be called in the gui
# object's constructor with the gui object as its only argument.
#
# When the gui object needs to offer the user choices, it will call the method
# context_choices() in the backend, which takes no arguments.
