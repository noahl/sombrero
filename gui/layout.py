#!/usr/bin/python

# Layout: arrange a series of Nodes on a canvas.
# each layout has an anchor, which is a Node that determines the layout's place
# in the canvas.
class Layout(object):
	def __init__(self, anchor, nodes = []):
		self.anchor = anchor
		self.nodes = nodes
		self.layout = None # cache the layout
	
	def addNode(self, node):
		self.nodes.append(node)
		self.layout = None # invalidate cached layout
	
	def addNodeAfter(self, prev, node):
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
			return layout
	
	# makeRelativeLayout: does the work for relativeLayout.
	# you should override this method if you want to make a Layout.
	# the base class will give you cached layouts for free
	def makeRelativeLayout(self):
		raise NotImplementedError()
	
	# adjust: adjust this layout's nodes in the canvas
	def adjust(self):
		(x, y) = self.anchor.coords()
		layout = self.relativeLayout()
		
		for (node, pos) in zip(self.nodes, layout):
			(rx, ry) = pos
			(nx, ny) = node.coords()
			node.moveBy((nx - x) - rx, (ny - y) - ry)

class ColumnLayout(Layout):
	def makeRelativeLayout(self):
		layout = []
		x = y = 0
		
		for n in self.nodes:
			layout.append((x, y))
			y += n.widget.winfo_reqheight()
			y += 10 # some padding
		
		return layout

class RowLayout(Layout):
	def makeRelativeLayout(self):
		layout = []
		x = y = 0
		
		for n in self.nodes:
			layout.append((x, y))
			x += n.widget.winfo_reqwidth()
			x += 10
		
		return layout

