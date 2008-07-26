#!/usr/bin/python

# gui.py: contains code for building a user interface in which the program
#         displays a tree to the user in a big canvas, which the user interacts
#         with through contextual menus.

from Tkinter import *
import layout

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
		if len(i) == 2:
			(lbl, call) = i
			menu.add_command(label = lbl, command = call)
		elif len(i) == 0:
			menu.add_separator()
		else:
			raise Exception("makeMenu can't understand menu item '" + i + "'")
	
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
		self.columnconfigure(1, weight = 0)
		self.rowconfigure(1, weight = 0)
		
		top = self.winfo_toplevel()
		top.rowconfigure(0, weight = 1)
		top.columnconfigure(0, weight = 1)
		
		self.canvas = Viewer(backend, self)
		self.canvas.grid(row = 0,
		                 column = 0,
		                 sticky=N+E+S+W)
		
		self.scrollX = Scrollbar(self, orient = HORIZONTAL,
		    command = self.canvas.xview)
		self.scrollX.grid(row = 1, column = 0, sticky = E+W)
		
		self.scrollY = Scrollbar(self, orient = VERTICAL,
		    command = self.canvas.yview)
		self.scrollY.grid(row = 0, column = 1, sticky = N+S)
		
		self.canvas["xscrollcommand"] = self.scrollX.set
		self.canvas["yscrollcommand"] = self.scrollY.set

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
	
	# Event handling functions:
	
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
	
	# Interface functions for the backend:
	
	def addNode(self, backend):
		if hasattr(self, "popup_loc") and self.popup_loc is not None:
			(x, y) = self.popup_loc
		else:
			(x, y) = (50, 50)
		
		Node(backend, self, x = x, y = y)

# a Node object handles the layout in the canvas of some other object, which is
# drawn in a canvas window.
class Node(object):
	def __init__(self, backend, canvas, x = 0, y = 0):
		self.canvas = canvas				
		self.widget = ProgramText(backend, canvas, self)
		# Node really shouldn't know about ProgramTexts, but it's okay
		# for now because the damage is localized.
		
		self.window = canvas.create_window(x, y, window=self.widget, anchor=NW)
				
		# if we add this handler here, clicks on the border of the text field will call
		# this *and* the canvas' right-click handler, even if add is "".
		#self.canvas.tag_bind(self.window, "<Button-3>", self.handle_right_click, add="")
		
		# right clicks in the text field get passed to the text field's right-click
		# callback, not the canvas window's, so don't bind them here.
		
		self.deps = [] # dependent layouts
	
	# for the layout that's placing this node:
	def setLayout(self, layout):
		self.layout = layout
	
	
	# there are three types of connected nodes: parents, children, and results.
	
	# in order to make everything work correctly, each Node needs to
	# know about its parent, child, and result Nodes if they are
	# displayed, so that the entire tree can shift together. however,
	# finding the boxes we need to move to make space should be done with
	# the canvas' find_... methods, so that we don't assume that we're the
	# only tree around.
	
	def coords(self):
		(x1, y1, x2, y2) = self.canvas.bbox(self.window)
		
		return (x1, y1)
	
	def moveBy(self, dx, dy):
		#print "node moving by", dx, dy
		self.canvas.move(self.window, dx, dy)
		for d in self.deps:
			d.adjust()
	
	def height(self):
		return self.widget.winfo_reqheight()
	
	def width(self):
		return self.widget.winfo_reqwidth()
	
	def bbox(self):
		return self.canvas.bbox(self.window)
	
	# add_anchored_layout: any node can serve as the anchor for a layout.
	# the anchor is the object whose position determines the position of
	# everything else in the layout
	
	# this method is called by the Layout object in its __init__ method.
	# you should never have to use this directly.
	def add_anchored_layout(self, layout):
		self.deps.append(layout)
	
	def delete(self):
		self.canvas.delete(self.window)
		if hasattr(self, "layout") and self.layout is not None:
			self.layout.absorb(self)
			self.layout.adjust()
		del self.widget
		del self.deps
	
	def __str__(self):
		return self.widget.backend.__str__()
	__repr__ = __str__

# ProgramText: a type of Text object to handle the actual display of a program.
# TODO: let people edit this object, and make it resize nicely when they do.
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
		
		# can't name them 'children' and 'result' or Tkinter will get mad.
		self.childLayout = None
		self.resultLayout = None
	
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
		pass
	
	def add_child(self, backend):
		if self.childLayout is None:
			self.childLayout = layout.ColumnLayout(self.node, self.canvas)
		
		self.childLayout.addNode(Node(backend, self.canvas))
		self.childLayout.adjust()
	
	def add_result(self, backend):
		#print "adding result", backend
		if self.resultLayout is None:
			self.resultLayout = layout.RowLayout(self.node, self.canvas)
		
		self.resultLayout.addNode(Node(backend, self.canvas))
		self.resultLayout.adjust()
	
	def delete(self):
		self.node.delete() # also removes us from the layout
		del self.node
		del self.childLayout
		del self.resultLayout
		self.destroy()
	
	# can't override either __str__ or __repr__ (or both?) for a tkinter
	# object

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
