### by Harrison Nguyen ###
# basic functions to convert cxl-based cmap to SQL create tables
"""
	Leave current notes about code here:
		1. at first, coded version that requires explicit definitions, if
		enough motivation/time, add in an agnostic version
		2. get raw cxl file working then can add in the URL for cmap if you want
		3. relations and attributes can't have the smae thing

	current methods:
		1. explicitly need to do everything ---> make sure it say has attributes


	test notes
		1. need to use ids to make connections because generic names are too much?
		2. make connections that go 2 deep at least if it's a linking
"""
import urllib2
import string
import sys
import json
import xml.etree.ElementTree as ET
import re
import argparse

# function to get necessary elements from 
# returns dictionary of necessary information
def getcxl(cxlfile):
	try:
		tree = ET.parse(cxlfile)
		root = tree.getroot()

		xmlns="{http://cmap.ihmc.us/xml/cmap/}"

		# get contents of the map
		cmap = root.find(xmlns+"map")
		
		# various containers
		relations, attributes, linking, connections = {}, [], [], {} 
		idmap = {}
		linkIDS = []

		# get all the concepts ---> then need to organize them
		# uses an id map to convert the ids to labels
		concepts = xmlns + "concept-list/" + xmlns + "concept" 
		concepts = cmap.findall(concepts)

		for concept in concepts:

			idmap[concept.get('id')] = concept.get('label')

			# get all the relations
			if concept.get('long-comment') == "relation":
				idmap[concept.get('id')] = concept.get('label')
				relations[concept.get('label')] = {'links' : [], 'attributes' : []}

			if concept.get('long-comment') == "attribute":
				idmap[concept.get('id')] = {
					'name': concept.get('label'),
					'type': concept.get('short-comment'),
					'constraint': None
				}
				attributes.append(concept.get('id'))

		# get all the linking phrases ---> this will tell what belongs to what
		lphrases = xmlns + "linking-phrase-list/" + xmlns + "linking-phrase" 
		lphrases = cmap.findall(lphrases)

		for phrase in lphrases:
			# create a separate one of JUST links to check later
			linkIDS.append(phrase.get('id'))
			# add to the idmap
			idmap[phrase.get('id')] = phrase.get('label')

		# get all the connections
		# current approach -->
		# check to see if either of the connections is from a linking phrase
		# if it is from a linking phrase ---> make it's own dictionary entry
		# thus, every linking should be connected to AT LEAST two concepts no matter what

		connects = xmlns + "connection-list/" + xmlns + "connection" 
		connects = cmap.findall(connects)
		for connect in connects:
			# is it the to-id?
			if connect.get('to-id') in linkIDS: 
				linkingID = connect.get('to-id')
				conceptID = connect.get('from-id')
			else:
				linkingID = connect.get('from-id')
				conceptID = connect.get('to-id')

			if str(idmap[conceptID]) in relations:
				relations[str(idmap[conceptID])]['links'].append(linkingID)
			else:
				idmap[conceptID]['linker'] = linkingID
				if 'attribute' not in idmap[linkingID]:
					idmap[conceptID]['constraint'] = idmap[linkingID]

		
		# now that we have the linking factors --> connection attributes to tables 
		for key in relations:
			for attr in attributes:
				if idmap[attr]['linker'] in relations[key]['links']:
					relations[key]['attributes'].append(idmap[attr])

		return relations
	# DICITONARY OF ATTRIBUTES
	# name of dictionary is the relation name
	# contains list of attributes


	except Exception as msg:
		print str(msg)
	   	sys.exit(1)


# use this to print out the statements
def createSQL(sqlInfo):
	whitespace = re.compile(r"\s+")
	create = ""	


	for key, infotables in sqlInfo.iteritems():
		base = "CREATE TABLE " + key + " ("
		for attrib in infotables['attributes']:
			base = base + re.sub(whitespace,"", attrib['name']) + " "

			# either int, varchar, or just char
			if 'int' in attrib['type']:
				base = base + "int" + ","
			elif 'var' in attrib["type"]:
				base = base + "varchar(" + re.sub("[^0-9]", "", attrib["type"]) + "),"
			else:
				getType = raw_input("No valid type given! please enter a type (var char with length or int): ")
				if 'int' in getType:
					base = base + "int" + ","
				else:
					base = base + "varchar(" + re.sub("[^0-9]", "", attrib["type"]) + "),"
		base = base[:-1]
		base = base + ");"
		create = create + base

	return create

def main():
	parser = argparse.ArgumentParser(description="Basic conversion of cmap cxl to sql tables.")
	getName = raw_input('please input file name (should be cxl in same folder): ')
	sqlInfo = getcxl(getName)
	print(createSQL(sqlInfo))


if __name__ == '__main__':
	main()