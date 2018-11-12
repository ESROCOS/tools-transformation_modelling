#!/usr/bin/python

import xml.etree.cElementTree as ET
import networkx as nx
from graphviz import Graph as gvGraph
import sys

# XML TAGS AND ATTRIBUTES
HEADER = "TransformationHeader"
STATIC_TF = "StaticTransformation"
DYN_TF = "DynamicTransformation"
REQ_TF = "RequestedTransformation"
REQ = "requested"
PROV = "provided"
EX  = "expressed_in"
TAR = "target" 

COMP_REF = "ComponentReference"
NAME = "name"

# CONFIGURABLE ATTRIBUTES
RENDER_PREFIX = "transforms_"
GRAPH_NAME = "Transformation"
DYNAMIC_EDGE_STYLE = "dashed"
STATIC_EDGE_STYLE = "solid"
REQUESTED_EDGE_STYLE = "dotted"
COLOR_EDGE_DEFAULT = "black"
COLOR_EDGE_VALID = "green" 
COLOR_EDGE_INVALID = "red"


# CHECK IF THERE IS A PATH FROM A TO B and return it
def existsPath(graph,a,b):
   if a in graph.frames and b in graph.frames:
     va = graph.frames[a]
     r = reachableNodes(graph, None, va)
   for f in r:
     print(f)
   
   for v in r:
     if v.name == b:
       return True
   
   return False
 
def isTree(graph):
  istree = True
  # depth first search to find cycles
  cy = isAcyclic(graph)
  print("is acyclic: ",cy)
  # depth first search to check connectedness
  cn = isConnected(graph)
  print("is connected: ",cn)
  return cy and cn 

# performs a depth first search from a arbitrary node, if the
# graph is a tree, the number of visited nodes will be equal
# to the number of all nodes in the graph
def isConnected(graph):
  c = len(reachableNodes(graph))
  if c == len(graph.frames):
    return True
  else:
    return False

# recursive function for depth search
def reachableNodes(graph,parent = None, root = None):

  if root is None: 
    root = list(graph.frames.values())[0]
     
  # store all subnodes including this
  visited = [root];
 
  print("visiting: "+root.name)

  # for all edges departing from the current node
  for adj in root.adjacencies():
    # pass over backwards-edge
    if adj == parent:
      continue
    # pass over already visited nodes
    elif adj in visited:
      continue
    # else check sub-tree with next node as root
    else:
      visited.extend(reachableNodes(graph, root, adj))
  return visited       

# CHECK IF GRAPH HAS CYCLES
def isAcyclic(graph,parent = None, root = None, visited = set()):
  
  # Trivial case, if the graph only has one node, it is a tree  
  if len(graph.frames)==1:
    return True

  if root is None: 
    root = list(graph.frames.values())[0]

  visited.add(root)
  
  # Flag to return later on
  allIsWell = True

  # for all edges departing from the current node
  for adj in root.adjacencies():

    # pass over backwards-edge
    if adj == parent:
      continue
    
    # if we meet an already visited node we
    # can abort because the graph is cyclic
    elif adj in visited:
      return False
    
    # else check sub-tree with next node as root
    else:
      allIsWell = allIsWell and isAcyclic(graph, root, adj, visited)

  return allIsWell       

# Define Frame
class Frame:

  def __init__ (self,name):
    self.name = name
    self.edges = set()
    self.color = "black"

  def __str__(self):
    return self.name

  def adjacencies(self):
    adjacencies = []
    #print len(self.edges)," adjacencies for ",self.name,":\n"
    for edge in self.edges:
      l = list(edge.frames)
      #print "\t",l[0].name+"<->"+l[1].name
      if l[0] == self:
        adjacencies.append(l[1])
      else:
        adjacencies.append(l[0])
    #print "\n"
    return adjacencies  

# Define Adjacency class (edge in graph)
class Edge:
  def __init__(self, frames, label = "", style="solid", color="black"):
    self.style = style
    self.color = color
    self.frames = frames
    self.label = label
    self.name = "" 

  def __str__(self):
    l = list(self.frames)
    
    return str(l[0])+"\t<->\t"+ str(l[1])

# Define Graph
class Graph:
  def __init__(self,name):
    self.name = name
    self.frames = {} 
    self.edges = set() 

  def __str__(self):
    s = self.name+":\nframes:\n"
    for frame in self.frames.values():
      s += "\t"+str(frame)+"\n "

    s += "\nedges:\n"

    for edge in self.edges:
      s += "\t"+str(edge)+"\n"

    return s  

# BUILD Transformation graph
def buildGraph(fileName):
  
  try:  
    tree = ET.parse(fileName)
    root = tree.getroot()
  except:
    raise

  requested_tree = root.find(REQ)
  provided_tree = root.find(PROV)

# build graph for provided transformations
  
  provided = buildGraphHelper(provided_tree,"provided")
  requested = buildGraphHelper(requested_tree,"requested")
 
  return [provided,requested]

def buildGraphHelper(tree, label):
   
  graph = Graph(label)

  for child in tree:
    # process header (to and from infos) 
    header = child.find(HEADER)

    tar_name = header.get(TAR)
    ex_name = header.get(EX)

    if ex_name in graph.frames:
      fr_ex = graph.frames[ex_name]
    else:
      fr_ex  = Frame(header.get(EX))
      graph.frames[fr_ex.name] = fr_ex

    if tar_name in graph.frames:
      fr_tar = graph.frames[tar_name]
    else:
      fr_tar  = Frame(header.get(TAR))
      graph.frames[fr_tar.name] = fr_tar 
    # process component ref if there is any
    comp_ref = child.find(COMP_REF)
    
    name = "" 
    if not comp_ref is None:
      name = comp_ref.get(NAME)
    
    # process edge type and associated style
    edge_style = STATIC_EDGE_STYLE  
    if child.tag == DYN_TF:
      edge_style = DYNAMIC_EDGE_STYLE
    if child.tag == REQ_TF:
      edge_style = REQUESTED_EDGE_STYLE

    tarToEx = Edge((fr_tar,fr_ex),name,edge_style) 
    
    #tarToEx.name = ""

    fr_tar.edges.add(tarToEx)
    fr_ex.edges.add(tarToEx)

    graph.edges.add(tarToEx)    

  return graph
# BUILD GRAPHVIZ GRAPH FROM TRANSFORMATION GRAPH

def renderGraph(graphs, display=False):
  #parent.graph_attr['rankdir'] = 'LR'
  
  filenames = {}

  for i, graph in enumerate(graphs):  
    g = gvGraph(comment=GRAPH_NAME, format='png')

    for frame in graph.frames.values():
      g.node(frame.name+"_"+str(i),frame.name)
     
    for edge in graph.edges:
      l = list(edge.frames)
      g.edge(l[0].name+"_"+str(i),l[1].name+"_"+str(i), style=edge.style, color=edge.color, label=" "+edge.label+"\n"+" "+edge.name)

    filename = RENDER_PREFIX+graph.name+'.gv'
    filenames[graph.name] = ""+filename+'.png'
    g.render(filename, view=display)

  return filenames
