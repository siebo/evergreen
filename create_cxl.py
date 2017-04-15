import csv
import sys
from xml.etree import ElementTree

ElementTree.register_namespace('', "http://cmap.ihmc.us/xml/cmap/")
ElementTree.register_namespace('dcterms', "http://purl.org/dc/terms/")
ElementTree.register_namespace('dc', "http://purl.org/dc/elements/1.1/")
ElementTree.register_namespace('vcard', "http://www.w3.org/2001/vcard-rdf/3.0#")

# Load CSV data
f = open(sys.argv[1], 'rt')

concepts = []

try:
    reader = csv.reader(f)
    row_count = 0
    
    #build list of unique concepts from CSV data
    for row in reader:
        if row_count != 0:
          subj = row[0]
          obj = row[1]
          for item in [subj, obj]:
            if item not in concepts:
              concepts.append(item)
            
        row_count += 1

finally:
    f.close()

# Open the blank CXL template
e = ElementTree.parse('template.cxl')
root = e.getroot()

children = []

for child in root:
  children.append(child)

print children

concept_list = root[1][0]

for concept in concepts:
  new = ElementTree.Element("concept", label=concept)
  concept_list.append(new)

e.write('output.cxl')