#!/usr/bin/python

import xml.etree.cElementTree as ET
from graphviz import Digraph
from sets import Set

HEADER = "TransformationHeader"
FILE = "transformations.xml"

tree = ET.parse(FILE)
root = tree.getroot()

requested = root.find("requested")
provided = root.find("provided")

frames = Set()
transforms = Set()

requested_transforms = Set()

for child in requested:
  header       = child.find(HEADER)
  requested_transforms.add((header.get("target"),header.get("expressed_in")))

for child in provided:
  header       = child.find(HEADER)
 
#  print header.tag,header.attrib
#  print header.get("target"),header.get("expressed_in")

  frames.add(header.get("target"))
  frames.add(header.get("expressed_in"))
    
  transforms.add((header.get("target"),header.get("expressed_in")))

print "frames:\t\t",frames

print "transforms:\t",transforms

print "requests:\t",requested_transforms

