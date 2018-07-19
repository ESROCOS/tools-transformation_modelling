#!/usr/bin/python

import xml.etree.cElementTree as ET
from graphviz import Graph as gvGraph
from sets import Set
import transformer_py as t
import sys

# XML TAGS AND ATTRIBUTES
HEADER = "TransformationHeader"
STATIC_TF = "StaticTransformation"
DYN_TF = "DynamicTransformation"
REQ = "requested"
PROV = "provided"
ex_in  = "expressed_in"
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
  
  if len(graph)==1:
    return True
  
  if root is None: 
    root = next(iter(graph.keys()))
    shouldCheckVisitedNumber = True    

  visited.add(root)
  
  # Flag to return later on
  allIsWell = True

  # for all edges departing from the current node
  for adj in graph[root]:
    # pass over backwards-edge
    if adj.target == parent:
      continue
    # if we meet an already visited node we
    # can abort because the graph is cyclic
    elif adj.target in visited:
      return False
    # else check sub-tree with next node as root
    else:
      allIsWell = allIsWell and isTree(graph, root, adj.target, visited)
 
  # if this was the original call, check if all nodes 
  # have been visited
  if shouldCheckVisitedNumber:
    allIsWell = allIsWell and len(graph) == len(visited)

  return allIsWell       


# Define Frame
class Frame:
  def __init__ (self,name):
    self.name = name

  def __str__(self):
    return self.name

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
    self.frames = Set()
    self.edges = Set()
  def __str__(self):
    return str(self.frames)+"\n"+str(self.edges)  

# BUILD Transformation graph
def buildGraph(fileName):
  tree = ET.parse(fileName)
  root = tree.getroot()

  requested_tree = root.find(REQ)
  provided_tree = root.find(PROV)

# build graph for provided transformations
  
  provided = Graph("provided transforms")
  requested = Graph("requested transforms")
 
  for child in provided_tree:
    header = child.find(HEADER)

    fr_tar  = Frame(header.get(tar))
    fr_ex = Frame(header.get(ex_in)) 
    edge_style = STATIC_EDGE_STYLE  
    if child.tag == DYN_TF:
      edge_style = DYNAMIC_EDGE_STYLE

    tarToEx = Edge((fr_tar,fr_ex),edge_style)

    print tarToEx

    provided.frames.add(fr_tar)
    provided.frames.add(fr_ex)
    provided.edges.add(tarToEx)    

  

  for child in requested_tree:
    header       = child.find(HEADER)

    fr_tar  = Frame(header.get(tar))
    fr_ex = Frame(header.get(ex_in)) 
   
    edge_style = REQUESTED_EDGE_STYLE

    tarToEx = Edge((fr_tar,fr_ex))
    
    requested.frames.add(fr_tar)
    requested.frames.add(fr_ex)
    requested.edges.add(tarToEx)    

  return [provided,requested]

# BUILD GRAPHVIZ GRAPH FROM TRANSFORMATION GRAPH

def renderGraph(graphs):
  parent = gvGraph(comment=GRAPH_NAME)
  
  for i, graph in enumerate(graphs):  
   
    with parent.subgraph(name="cluster_"+graph.name) as sg: 
      sg.attr(label=graph.name)

      for frame in graph.frames:
        sg.node(frame.name+"_"+str(i),frame.name)
     
      for edge in graph.edges:
        l = list(edge.frames)
        sg.edge(l[0].name+"_"+str(i),l[1].name+"_"+str(i), style=edge.style, color=edge.color)

  parent.render('transforms.gv', view=True)


