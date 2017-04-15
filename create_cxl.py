import csv
import sys
import xml.etree.ElementTree

# Load CSV data
f = open(sys.argv[1], 'rt')

concepts = []

try:
    reader = csv.reader(f)
    row_count = 0
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
e = xml.etree.ElementTree.parse('template.cxl')
root = e.getroot()

# add concept nodes to the elementtree
for child in root:
  if child.tag == '{http://cmap.ihmc.us/xml/cmap/}map':
    for concept in concepts:
      new = xml.etree.ElementTree.Element("concept", label=concept)
      child.append(new)

e.write('output.cxl')