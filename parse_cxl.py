import xml.etree.ElementTree
e = xml.etree.ElementTree.parse('test.cxl')
root = e.getroot()

# get a handle on the root tag and attribs
root_tag = root.tag
root_attribs = root.attrib

# build a list of dicts with tag and attrib for 
# each child tag under the root node
root_children = []
for child in root:
    res_dict = {}
    res_dict['tag'] = child.tag
    res_dict['attrib'] = child.attrib
    root_children.append(res_dict)

# test appending node to elementtree
for child in root:
  if child.tag == '{http://cmap.ihmc.us/xml/cmap/}map':
    new = xml.etree.ElementTree.Element("new-item", name="Picolina")
    child.append(new)

e.write('output.cxl')