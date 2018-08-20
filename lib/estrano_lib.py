#!/usr/bin/python

import xml.etree.cElementTree as ET
from graphviz import Graph as gvGraph
from sets import Set
#import transformer_py as t
import sys

# XML TAGS AND ATTRIBUTES
HEADER = "TransformationHeader"
STATIC_TF = "StaticTransformation"
DYN_TF = "DynamicTransformation"
REQ_TF = "RequestedTransformation"
REQ = "requested"
PROV = "provided"
ex  = "expressed_in"
tar = "target" 

# CONFIGURABLE ATTRIBUTES
GRAPH_NAME = "Transformation"
DYNAMIC_EDGE_STYLE = "dashed"
STATIC_EDGE_STYLE = "solid"
REQUESTED_EDGE_STYLE = "dotted"
COLOR_EDGE_VALID = "green" 
COLOR_EDGE_INVALID = "red"
 
# CHECK IF GRAPH IS A TREE
def isTree(graph,parent = None, root = None, visited = Set()):
  
  shouldCheckVisitedNumber = False
  
  if len(graph.frames)==1:
    return True
   
  if root is None: 
    root = graph.frames.values()[0]
    shouldCheckVisitedNumber = True    
  
  vs = ""
  for v in visited:
    vs+=str(v)+", "
  
  adjs = ""
  for a in root.adjacencies():
    adjs+=str(a)+", " 

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
#      print "current node: "+str(root)+"\nadjacents:"+adjs+"\nvisited: "+vs+"\n"+"next node: "+adj.name+" already visited"
      return False
    # else check sub-tree with next node as root
    else:
#      print "current node: "+str(root)+"\nadjacents:"+adjs+"\nvisited: "+vs+"\n"+"next node: "+adj.name+"\n"
      allIsWell = allIsWell and isTree(graph, root, adj, visited)
 
  # if this was the original call, check if all nodes 
  # have been visited
  if shouldCheckVisitedNumber:
    allIsWell = allIsWell and len(graph.frames) == len(visited)
#    print "visited all subtrees, have I seen the whole graph?",allIsWell

  return allIsWell       


# Define Frame
class Frame:

  def __init__ (self,name):
    self.name = name
    self.edges = Set()

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
  def __init__(self, frames, style="solid", color="black"):
    self.style = style
    self.color = color
    self.frames = frames

  def __str__(self):
    l = list(self.frames)
    
    return str(l[0])+"\t<->\t"+ str(l[1])

# Define Graph
class Graph:
  def __init__(self,name):
    self.name = name
    self.frames = {} 
    self.edges = Set() 

  def __str__(self):
    s = self.name+":\nframes:\n"
    for frame in self.frames.values():
      s += "\t"+str(frame)+"\n "

    s += "\nedges:\n"

    for edge in self.edges.values():
      s += "\t"+str(edge)+"\n"

    return s  

# BUILD Transformation graph
def buildGraph(fileName):
  tree = ET.parse(fileName)
  root = tree.getroot()

  requested_tree = root.find(REQ)
  provided_tree = root.find(PROV)

# build graph for provided transformations
  
  provided = buildGraphHelper(provided_tree,"provided transforms")
  requested = buildGraphHelper(requested_tree,"requested transforms")
 
  return [provided,requested]

def buildGraphHelper(tree, label):
   
  graph = Graph(label)

  for child in tree:
    header = child.find(HEADER)

    tar_name = header.get(tar)
    ex_name = header.get(ex)

    if ex_name in graph.frames:
      fr_ex = graph.frames[ex_name]
    else:
      fr_ex  = Frame(header.get(ex))
      graph.frames[fr_ex.name] = fr_ex

    if tar_name in graph.frames:
      fr_tar = graph.frames[tar_name]
    else:
      fr_tar  = Frame(header.get(tar))
      graph.frames[fr_tar.name] = fr_tar 

    edge_style = STATIC_EDGE_STYLE  
    if child.tag == DYN_TF:
      edge_style = DYNAMIC_EDGE_STYLE
    if child.tag == REQ_TF:
      edge_style = REQUESTED_EDGE_STYLE

    tarToEx = Edge((fr_tar,fr_ex),edge_style) 

    fr_tar.edges.add(tarToEx)
    fr_ex.edges.add(tarToEx)

    graph.edges.add(tarToEx)    

  return graph
# BUILD GRAPHVIZ GRAPH FROM TRANSFORMATION GRAPH

def renderGraph(graphs):
  parent = gvGraph(comment=GRAPH_NAME)
  
  for i, graph in enumerate(graphs):  
   
    with parent.subgraph(name="cluster_"+graph.name) as sg: 
      sg.attr(label=graph.name)

      for frame in graph.frames.values():
        sg.node(frame.name+"_"+str(i),frame.name)
     
      for edge in graph.edges:
        l = list(edge.frames)
        sg.edge(l[0].name+"_"+str(i),l[1].name+"_"+str(i), style=edge.style, color=edge.color)

  parent.render('transforms.gv', view=True)


