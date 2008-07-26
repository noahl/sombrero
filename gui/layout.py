#!/usr/bin/python

from Tkinter import *

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
	
	# decorateLayout: override this method in a subclass to do draw extra
	# stuff after the nodes are layed out, like drawing arrows.
	def decorateLayout(self):
		pass
	
	# Note: if you wanted to add animation to Sombrero, this is where you
	# would do it. Just change the layout.adjust() method so that instead
	# of moving everything immediately, it keeps track of how everything
	# needs to move, and then move the nodes gradually over many frames.
	
	# delete: remove a node from our list
	def delete(self, node):
		self.nodes.remove(node)
		print "shortened layout:", self.nodes
	
	def __str__(self):
		return "Layout " + str(id(self))
	__repr__ = __str__

class ColumnLayout(Layout):
	def makeRelativeLayout(self):
		layout = []
		x = 18 # indent. 20 pixels also looks good.
		y = self.anchor.height() + 10
		
		for n in self.nodes:
			layout.append((x, y))
			y += n.height()
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
			x += n.width()
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

