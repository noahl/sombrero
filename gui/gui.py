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

# PopupMenu: has a button which pops up a menu of choices. the text of the
# button is whatever choice is selected.
# this class acts kind of like a Tkinter widget, but really isn't.
class PopupMenu(object):
	def __init__(self, backend, master = None):
		self.backend = backend
		self.button = Button(master, text = backend.default_text(),
		                     command = self.popup)
	def popup(self):
		choices = self.backend.context_choices()
		menu = makeMenu(self.button, *choices)
		self.popup = popupMenu(self.button.winfo_rootx(),
		                       self.button.winfo_rooty(),
		                       menu)
	def grid(self, *args, **kwargs):
		self.button.grid(*args, **kwargs)

# TODO: I got the idea for an App class from the NMT Tkinter tutorial, but I
#       think it might be outdated or just wrong. I should check up on this and
#       then possibly change it.
# Note: the App is not a real gui class. It doesn't register itself with its
# backend, because it doesn't have any clear purpose in the program. It should
# probably go away.
class App(Frame):
	def __init__(self, backend, filebackend, master=None):
		Frame.__init__(self, master)
		
		self.grid(sticky=N+S+E+W)
		self.columnconfigure(0, weight = 1)
		self.rowconfigure(0, weight = 1)
		self.columnconfigure(1, weight = 0)
		self.rowconfigure(1, weight = 0)
		self.columnconfigure(2, weight = 0)
		
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
		
		self.rightframe = Frame(self)
		self.rightframe.grid(row = 0, column = 3, rowspan = 2,
		                     sticky = N+E+S+W)
		
		self.importbutton = Button(self.rightframe,
		                           command = filebackend.import_file,
		                           text = "Import A Hat Trace File")
		self.importbutton.grid(row = 0, column = 0, sticky=N+E+W) # sticky N?
		
		self.fileframe = Frame(self.rightframe)
		self.fileframe.grid(row = 1, column = 0, sticky = N+E+W)
		
		self.filelabel = Label(self.fileframe, text = "File:")
		self.filelabel.grid(row = 0, column = 0, sticky = W)
		
		self.filemenuchooser = PopupMenu(filebackend, self.fileframe)
		self.filemenuchooser.grid(row = 0, column = 1, sticky = E+W)
		
		self.gobutton = Button(self.rightframe, text = "Go",
		                       command = filebackend.go)
		self.gobutton.grid(row = 2, column = 0, sticky = N+E+W)

# TODO: why is viewer a separate class? This could all be part of App.
class Viewer(Canvas):
	def __init__(self, backend, master=None):
		Canvas.__init__(self, master, state = NORMAL, takefocus = 1,
		                background = "white")
		self.backend = backend
		if hasattr(backend, "setgui"):
			backend.setgui(self)
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
		
		layout.Node(ProgramText(backend, self), self, x = x, y = y)

# ProgramText: a type of Text object to handle the actual display of a program.
# TODO: let people edit this object, and make it resize nicely when they do.
class ProgramText(Text):
	def __init__(self, backend, canvas):
		self.backend = backend
		if hasattr(backend, "setgui"):
			backend.setgui(self)
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
	
	def setnode(self, node):
		self.node = node
	
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
		
		self.childLayout.addNode(layout.Node(ProgramText(backend, self.canvas),
		                              self.canvas))
		self.childLayout.adjust()
	
	def add_result(self, backend):
		#print "adding result", backend
		if self.resultLayout is None:
			self.resultLayout = layout.RowLayout(self.node, self.canvas)
		
		self.resultLayout.addNode(layout.Node(ProgramText(backend, self.canvas),
		                               self.canvas))
		self.resultLayout.adjust()
	
	def delete(self):
		self.node.delete() # also removes us from the layout
		del self.node
		del self.childLayout
		del self.resultLayout
		self.destroy()
	
	# can't override either __str__ or __repr__ (or both?) for a tkinter
	# object

def gui_go(backend, filebackend):
	app = App(backend, filebackend)
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
