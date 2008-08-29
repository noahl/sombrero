#!/usr/bin/python

# layout.py: this file handles placing objects on a canvas so that they have
# some desired relationships to each other and don't overlap. As a bonus, we
# can also draw arrows between them.

# The Node class represents an object drawn on a canvas, and it has a Tkinter
# canvas window which it uses to display it's widget. The Layout object manages
# a group of Nodes that all need to be arranged in some way, like in a line.
# Every Layout has an anchor node, which it places all of its widgets relative
# to. No layout can place its own anchor node, and no layout *should* place
# either the anchor node of its anchor's layout, or any other anchor node
# farther back, etc. In this way, we form a tree of nodes, with Layouts at each
# branching, and each node is placed in relation to its parent in the tree.

from Tkinter import *

# Note on the layout algorithm: any layout algorithm needs to make sure that
# nodes don't overlap on the canvas. The *right* way to do this, it seems to
# me, is to do as little adjustment as possible. You could notice when two
# nodes overlap, then use a fairly simple algorithm to find their lowest common
# parent in the tree of layout objects and adjust that object's layout.
# What I'm going to do right now is a quick hack to get a similar effect for a
# lot less effort. If any two nodes overlap, I'm just going to adjust the
# entire tree. This will require a lot more computation for most cases, and
# will not work if the two nodes are in different trees. It will, however, not
# take much coding right now.
# Update: it's working sort of, but I don't know why. I suspect Tkinter's doing
# something I don't understand, so it might stop working suddenly, or it might
# be using a less-efficient algorithm than the one I wanted that happens to
# produce correct results (I suspect this is so). It would be really great if I
# or somebody else figured out what was going on and made this work correctly.

# _nodesById: a dictionary of Nodes whose keys are the IDs of the canvas window
# objects. we use this to find a node from its ID.
_nodesById = dict()

# a Node object handles the layout in the canvas of some other object, which is
# drawn in a canvas window.
class Node(object):
	def __init__(self, widget, canvas, x = 0, y = 0):
		self.canvas = canvas				
		self.widget = widget
		if hasattr(widget, "setnode"):
			widget.setnode(self)
		
		self.window = canvas.create_window(x, y, window=self.widget, anchor=NW)
		
		_nodesById[self.window] = self
				
		# if we add this handler here, clicks on the border of the text field will call
		# this *and* the canvas' right-click handler, even if add is "".
		#self.canvas.tag_bind(self.window, "<Button-3>", self.handle_right_click, add="")
		
		# right clicks in the text field get passed to the text field's right-click
		# callback, not the canvas window's, so don't bind them here.
		
		self.deps = [] # dependent layouts		
	
	# do_init: do all the initialization things that use our connections to
	# other objects.
	#
	# do_init solves the following problem: a Sombrero program state is a
	# collection of objects with connections between them. The objects
	# partition the global state into little sub-areas, which helps keep it
	# manageable. Many of these objects have two-way connections with other
	# objects, so they can send messages back and forth. However, this
	# creates a problem when making a new object: we can't connect an
	# object to other objects until we have it, and we can't have it until
	# *after* we've called its __init__ method. So the init method has to
	# execute in a state where not all the connections that should be made
	# have been made properly yet. Therefore, it can't do initialization
	# that involves calling methods in other objects that then call back
	# into it, because those connections have not been set up yet. We could
	# do initialization in the set* methods, which are used to set up these
	# connections, but that is inelegant, and also depends on the order
	# those functions are called in, which is a bad idea. The do_init
	# method solves this problem in a better way. do_init should be called
	# after an object has been made and all relevant connections to other
	# objects have been set up. do_init should then finish whatever setup
	# __init__ couldn't do, and leave the object ready for use.
	
	# TODO: it might be possible to get around the initialization-timing
	# restriction mentioned above through the __new__ method, or possibly
	# the new() built-in function. look into this.
	
	def do_init(self):
		if hasattr(self, "layout"):
			self.layout.adjust()
		
		# the following lines work, but I don't know why. the
		# self.adjustAll() call at the bottom here will always work,
		# for reasons that are quite clear, but may be slower than
		# this. I'm using this for now, but if it ever gets weird, just
		# comment this stuff out and uncomment the call at the bottom
		# of this method.
		overlaps = self.canvas.find_overlapping(*self.canvas.bbox(self.window))
		if len(overlaps) > 1: # we'll always find ourselves.
			#print "Overlap! Nodes:", [_nodesById[n]
			#                           for n in overlaps
			#                           if n in _nodesById]
			#print "Non-nodes:", [n for n in overlaps
			#                       if n not in _nodesById]
			self.adjustAll()
		
		#self.adjustAll()
	
	# for the layout that's placing this node:
	def setLayout(self, layout):
		self.layout = layout
	
	
	# in order to make everything work correctly, each Node needs to
	# know about whatever nodes are connected, so that the entire tree can
	# shift together. however, finding the boxes we need to move to make
	# space should be done with the canvas' find_... methods, so that we
	# don't assume that we're the only tree around.
	
	def coords(self):
		(x1, y1, x2, y2) = self.canvas.bbox(self.window)
		
		return (x1, y1)
	
	def moveBy(self, dx, dy):
		self.canvas.move(self.window, dx, dy)
		
		for d in self.deps:
			d.adjust()
	
	# plain height, width, and bbox just refer to our widget
	
	def height(self):
		return self.widget.winfo_reqheight()
	
	def width(self):
		return self.widget.winfo_reqwidth()
	
	def bbox(self):
		return self.canvas.bbox(self.window)
	
	# deps_{height, width, bbox} refer to us and all of our dependents
	def deps_height(self):
		x1, y1, x2, y2 = self.deps_bbox()
		
		return y2 - y1
	
	def deps_width(self):
		x1, y1, x2, y2 = self.deps_bbox()
		
		return x2 - x1
	
	def deps_bbox(self):
		box = self.bbox()
		
		for d in self.deps:
			db = d.deps_bbox()
			box = mergeBoxes(box, db)
		
		return box
	
	# adjustAll: the method we use to implement the hack described at the
	# top of the file. this passes the adjustAll call up the tree of nodes.
	def adjustAll(self):
		if hasattr(self, "layout"):
			self.layout.adjustAll()
			# XXX: OPEN QUESTION: should we also call adjustAll on
			# all the layouts in self.deps (and have them do
			# similar calls for their child nodes)?
		else:
			x0, y0, x1, y1 = self.deps_bbox()
			self.canvas["scrollregion"] = (0, 0, x1, y1)
			# the last line was based on the IDLE source code, file
			# TreeWidget.py in the top-level source directory
			# ("idlelib" in the "Lib" directory in the Python-2.6b1
			# source tree), line 172.
	
	# add_anchored_layout: any node can serve as the anchor for a layout.
	# the anchor is the object whose position determines the position of
	# everything else in the layout.
	
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

# Layout: arrange a series of Nodes on a canvas.
# each layout has an anchor, which is a Node that determines the layout's place
# in the canvas.
class Layout(object):
	def __init__(self, anchor, canvas, nodes = []):
		if anchor in nodes:
			raise Exception("A Layout can't place its own anchor!", anchor, nodes)

		self.anchor = anchor
		anchor.add_anchored_layout(self)
		self.canvas = canvas
		self.nodes = nodes[:] # copy the node list. default arguments
		                      # are evaluated once per *definition*
		                      # (and this covers other cases, too).
		self.layout = None # cache the layout
	
	def do_init(self):
		pass
	
	def addNode(self, node):
		self.nodes.append(node)
		
		if node is self.anchor:
			raise Exception("A Layout can't place its own anchor!")
		
		if hasattr(node, "setLayout"):
			node.setLayout(self)
		
		self.layout = None # invalidate cached layout
		#print "added a node to a layout"
	
	def addNodeAfter(self, prev, node):
		if node is self.anchor:
			raise Exception("A Layout can't place its own anchor!")
		
		try:
			i = self.nodes.index(prev)
		except ValueError:
			self.nodes.append(node)
		else:
			self.nodes.insert(i, node)
		finally:
			self.layout = None
	
	# absorb: take the given node, absorb its dependent layouts
	def absorb(self, node):
		print self, "absorbing", node
		for d in node.deps:
			self.nodes.extend(d.nodes)
			del d.anchor
			del d.nodes
		self.layout = None
		print "extended layout:", self.nodes

	# relativeLayout: return a list of (x, y) pairs, starting with (0, 0)
	def relativeLayout(self):
		if self.layout is not None:
			return self.layout
		else:
			layout = self.makeRelativeLayout()
			self.layout = layout
			#print "made new relative layout", layout
			return layout
	
	# makeRelativeLayout: does the work for relativeLayout.
	# you should override this method if you want to make a Layout.
	# the base class will give you cached layouts for free
	def makeRelativeLayout(self):
		raise NotImplementedError()
	
	# adjust: adjust this layout's nodes in the canvas
	def adjust(self):
		#print "adjusting layout"
		(x, y) = self.anchor.coords()
		layout = self.relativeLayout()
		
		for (node, pos) in zip(self.nodes, layout):
			(rx, ry) = pos
			(nx, ny) = node.coords()
			#print "moving node", node
			node.moveBy(rx - (nx - x), ry - (ny - y))
		
		self.decorateLayout()

	# Note: if you wanted to add animation to Sombrero, this is where you
	# would do it. Just change the layout.adjust() method so that instead
	# of moving everything immediately, it keeps track of how everything
	# needs to move, and then move the nodes gradually over many frames.
	
	# adjustAll: this is the method that implements the hackish layout
	# algorithm documented at the top of the page. this adjusts the part of
	# the tree above us, and then calls our own adjust() method.
	def adjustAll(self):
		self.anchor.adjustAll()
		self.layout = None # invalidate our cached layout.
		self.adjust()
	
	# decorateLayout: override this method in a subclass to do draw extra
	# stuff after the nodes are layed out, like drawing arrows.
	def decorateLayout(self):
		pass
	
	# deps_bbox: return the merged bounding boxes of all the nodes that
	# this layout manages.
	def deps_bbox(self):
		box = self.nodes[0].deps_bbox()
		
		for n in self.nodes[1:]:
			nb = n.deps_bbox()
			box = mergeBoxes(box, nb)
		
		return box
	
	# delete: remove a node from our list
	def delete(self, node):
		self.nodes.remove(node)
		print "shortened layout:", self.nodes
	
	def __str__(self):
		return "Layout " + str(id(self))
	__repr__ = __str__

# mergeBoxes: take two bounding boxes, and return one box that includes both
# areas.
def mergeBoxes(b1, b2):
	(x1, y1, x2, y2) = b1
	(x3, y3, x4, y4) = b2
	
	return (min(x1, x3), min(y1, y3), max(x2, x4), max(y2, y4))

class ColumnLayout(Layout):
	def makeRelativeLayout(self):
		layout = []
		x = 18 # indent. 20 pixels also looks good.
		y = self.anchor.height() + 10
		
		for n in self.nodes:
			layout.append((x, y))
			y += n.deps_height()
			y += 10 # some padding
		
		return layout
	
	def decorateLayout(self):
		if hasattr(self, "lines"):
			for l in self.lines:
				self.canvas.delete(l)
		self.lines = []
		(ax1, ay1, ax2, ay2) = self.anchor.bbox()
		x = ax1 + 5
		y = ay2
		for n in self.nodes:
			(nx1, ny1, nx2, ny2) = n.bbox()
			self.lines.append(
			  self.canvas.create_line(x, y, # a two-segment line
			                          x, (ny1+ny2)/2,
			                          nx1, (ny1+ny2)/2,
			                          arrow=LAST))
			y = (ny1+ny2)/2

class RowLayout(Layout):
	def makeRelativeLayout(self):
		layout = []
		x = self.anchor.width() + 10
		y = 0
		
		for n in self.nodes:
			layout.append((x, y))
			x += n.deps_width()
			x += 10
		
		return layout
	
	def decorateLayout(self):
		#print "decorateLayout called"
		#print "len(self.nodes) is", len(self.nodes)
		if hasattr(self, "lines"):
			for l in self.lines:
				self.canvas.delete(l)
		self.lines = []
		(ax1, ay1, ax2, ay2) = self.anchor.bbox()
		(bx1, by1, bx2, by2) = self.nodes[0].bbox()
		self.lines.append(
		  self.canvas.create_line(ax2, (ay1+ay2)/2, bx1, (by1+by2)/2,
			                  arrow=LAST, fill="black", width=2))
		for i in range(0, len(self.nodes)-1):
			#print "drawing line"
			(ax1, ay1, ax2, ay2) = self.nodes[i].bbox()
			(bx1, by1, bx2, by2) = self.nodes[i+1].bbox()
			
			self.lines.append(
			  self.canvas.create_line(ax2, (ay1+ay2)/2, bx1, (by1+by2)/2,
			                          arrow=LAST, fill="black", width=2))

