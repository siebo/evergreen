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

e.write('output.cxl')