#!/usr/bin/python

# Layout: arrange a series of Nodes on a canvas.
# each layout has an anchor, which is a Node that determines the layout's place
# in the canvas.
class Layout(object):
	def __init__(self, anchor, nodes = []):
		if anchor in nodes:
			raise Exception("A Layout can't place its own anchor!", anchor, nodes)

		self.anchor = anchor
		anchor.add_anchored_layout(self)				
		self.nodes = nodes[:] # copy the node list. default arguments
		                      # are evaluated once per *definition*
		                      # (and this covers other cases, too).
		self.layout = None # cache the layout
	
	def addNode(self, node):
		self.nodes.append(node)
		
		if node is self.anchor:
			raise Exception("A Layout can't place its own anchor!")
		
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

class ColumnLayout(Layout):
	def makeRelativeLayout(self):
		layout = []
		x = 0
		y = self.anchor.height() + 10
		
		for n in self.nodes:
			layout.append((x, y))
			y += n.height()
			y += 10 # some padding
		
		return layout

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

