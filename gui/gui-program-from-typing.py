#!/usr/bin/python

from Tkinter import *

class App(Frame):
	def __init__(self, master=None, **options):
		Frame.__init__(self, master, **options)
		
		self.grid(sticky=N+S+E+W)
		self.columnconfigure(0, weight = 1)
		self.rowconfigure(0, weight = 1)
		
		top = self.winfo_toplevel()
		top.rowconfigure(0, weight = 1)
		top.columnconfigure(0, weight = 1)
		
		self.canvas = Viewer(self,
		                     background = "white")
		self.canvas.grid(row = 0,
		                 column = 0,
		                 sticky=N+E+S+W)

class Viewer(Canvas):
	def __init__(self, master=None, **options):
		Canvas.__init__(self, master, **options)
		self.bind("<KeyPress>", self.handle_keypress, add="+")
	
	def handle_keypress(self, event):
		print "Canvas getting keypress!"
		if hasattr(event, "char"):
			self.programFromChar(event)
	
	# programFromChar: called when someone starts typing a program in
	def programFromChar(self, event):
		# We start a new program box in response to typing. However, it
		# should act "as if" the box had been there since before the
		# user started typing
		
		p = ProgramBox(self) # make a new program box
		oldfocus = self.focus_get()
		p.cmdfield.focus_set() # give the box's command field the focus
		newfocus = self.focus_get()
		
		oldcfocus = self.focus() # "cfocus" = "canvas focus"
		self.focus(p.window)
		newcfocus = self.focus()
		
		print "Old focus:", oldfocus, "New focus:", newfocus
		print "Old cfocus:", oldcfocus, "New cfocus:", newcfocus
		
		if oldfocus == newfocus and oldcfocus == newcfocus:
			print "Focus stayed the same:", newfocus
			print "My focus:", self.focus()
			self.quit()
			raise Exception, "TCL/TK Fails"
		
		print "Generating a keypress of '", str(event.char), "'"
		
		# can't send all of the event's options, because some don't work.
		app.event_generate("<KeyPress-"+str(event.char)+">")

class ProgramBox(object):
	def __init__(self, canvas = None, **options):
		self.canvas = canvas
		self.cmdfield = Text(canvas, **options)
		self.window = canvas.create_window(20, 20, window=self.cmdfield)
		print "text name:", self.cmdfield
		print "window id:", self.window
	
	def takeFocus(self):
		self.canvas.focus(self.window)

app = App(takefocus = 0)
app.master.title("Sombrero")
app.canvas.focus_set()
app.mainloop()
