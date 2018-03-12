import pandas as pd
import numpy as np
from xml.etree import ElementTree
from string import ascii_uppercase
from string import digits
from random import SystemRandom


ElementTree.register_namespace('', "http://cmap.ihmc.us/xml/cmap/")
ElementTree.register_namespace('dcterms', "http://purl.org/dc/terms/")
ElementTree.register_namespace('dc', "http://purl.org/dc/elements/1.1/")
ElementTree.register_namespace('vcard', "http://www.w3.org/2001/vcard-rdf/3.0#")

# TESTING PHASE
# TODO: MAKE LINKAGES FOR FOREIGN KEYS

def createCmapID():
  options = ascii_uppercase + digits
  i1 = ''.join(SystemRandom().choice(options) for _ in range(9))
  i2 = ''.join(SystemRandom().choice(options) for _ in range(6))
  i3 = ''.join(SystemRandom().choice(options) for _ in range(2))
  new_id = "%s-%s-%s" % (i1,i2,i3)
  return new_id


# Reads in csv (later SQL queries) and converts them to dataframes for returning
# INPUT: file path to csv file/SQL query
# OUTPUT: dataframe containing information
def read_CSV(filename):
  try:
    # Load csv into a pandas dataframe object
    df = pd.read_csv(filename)
    return df
  except FileNotFoundError:
    print ("CSV File does not exist!")
    exit()

# Gathers data from csv file/query, assigns cid to each element, and manipulates dataframe
# INPUT: pandas dataframe
# OUTPUT: pandas dataframe with additional cid columns
def writeCXL(df_SQL, cxl):
  #dfLength = len(df)
  
  # Open the blank CXL template
  e = ElementTree.parse('template.cxl')
  root = e.getroot()
  
  # root [0][0] corresponds to res-meta tag
  # root [1][0] corresponds to concept-list tag  
  concept_list = root[1][0] # For subjects and objects
  linking_list = root[1][1] # For linking words
  connection_list = root[1][2] # For actual connection (the little lines)
  
  # appearance lists
  concept_appearance_list = root[1][3]
  linking_appearance_list = root[1][4] 
  connection_appearance_list = root[1][5]
  
  
  # Dictionary to keep track of table names and its IDs since there is no table for it
  tableDict = dict()
  for tableName in df_SQL["Table_Name"].unique():
    tableDict[tableName] = createCmapID()
  
  # Keeping track of linking phrase and connection information for cxl write
  df_LinkingPhraseInfo = pd.DataFrame(columns=["Linking Phrase", "Linking Phrase ID", "Table_Name"])
  #df_ConnectionInfo = pd.DataFrame(columns=["Connection ID", "To", "From"])
  
  # Processing tables and writing to cxl file at the same time
  # Write first to cxl, then process values into tables for later lookup
  for table in tableDict:
    addConcepts(concept_list, concept_appearance_list, "concept", {'id': tableDict[table], 'label': table})
    df_TableName = df_SQL[df_SQL.loc[:, "Table_Name"] == table]
    
    # Go through each row in the table containing column info to put in connections and linking phrases one by one
    for row in df_TableName.itertuples():
      addConcepts(concept_list, concept_appearance_list, "concept", {'id': row.ID, 'label': row.Column_Name})
      
      # Isolating linking phrases by table name for simplicity        
      df_LinkingPhraseSubset = df_LinkingPhraseInfo[df_LinkingPhraseInfo.loc[:, 'Table_Name'] == table]
      
      # To match cmap terminology
      if "foreign key" in row.Type:
        linkingPhraseLabel = "has FOREIGN KEY"
      else:
        linkingPhraseLabel = "has " + row.Type
      
      # If there is a linking phrase for "has attribute" that exists for the table, retrieve it
      if df_LinkingPhraseSubset[df_LinkingPhraseSubset.loc[:, "Linking Phrase"] == linkingPhraseLabel].shape[0] > 0:
        linkingPhraseLocation = df_LinkingPhraseSubset[df_LinkingPhraseSubset.loc[:, "Linking Phrase"] == linkingPhraseLabel].index.tolist()
        
        # Append to connection list, connecting concept -> linking phrase -> concept using two connections
        addConnection(connection_list, connection_appearance_list, createCmapID(), tableDict[table], df_LinkingPhraseSubset.at[linkingPhraseLocation[0], "Linking Phrase ID"])
        addConnection(connection_list, connection_appearance_list, createCmapID(), df_LinkingPhraseSubset.at[linkingPhraseLocation[0], "Linking Phrase ID"], row.ID)
      
      # Else add the linking phrase to the dataframe for lookup and add linking phrase to the cxl file
      else:
        linkingPhraseID = createCmapID()
        df_LinkingPhraseInfo.loc[df_LinkingPhraseInfo.shape[0]] = [linkingPhraseLabel, linkingPhraseID, table]
        addConcepts(linking_list, linking_appearance_list, "linking-phrase", {'id': linkingPhraseID, 'label': linkingPhraseLabel})
        # Append to connection list, connecting concept -> linking phrase -> concept using two connections
        addConnection(connection_list, connection_appearance_list, createCmapID(), tableDict[table], linkingPhraseID)
        addConnection(connection_list, connection_appearance_list, createCmapID(), linkingPhraseID, row.ID)
       
  
  # TODO: Connect Foreign keys
  df_ForeignKey = df_SQL[df_SQL["Type"].str.contains('foreign key')]
  for foreign_row in df_ForeignKey.itertuples():
    foreignTable = foreign_row.Type.split("::")[1]
    foreignColumn = foreign_row.Type.split("::")[2]
    
    
  indent(root)
  e.write('output.cxl')      
 
  
# Assigns CID to the appropriate concept
# INPUT: A dataframe row, a cid dictionary, column to retrieve dictionary query from
# OUTPUT: matching cid to concept
def assignConceptCID(row, referenceDict, colName):
  return referenceDict[row[colName]]

# Adds formatted XML elements for the concepts and appearances portions of cxl file
# INPUT: XML filepath parser for concept, an XML filepath parser for the appearance, a string representing the concept, a dictionary with attributes for the element
def addConcepts(concept_list, concept_appearance_list, name, attribute_list):
  newConcept = ElementTree.Element(name, attrib=attribute_list)
  appearance_Name = name + "-appearance"
  newAppearance = ElementTree.Element(appearance_Name, attrib={'id': attribute_list['id'], "x":"0", "y":"0", "width":"80", "height":"25"})
  
  concept_list.append(newConcept)
  concept_appearance_list.append(newAppearance)

# Adds connection and connection appearance elements to make links for the cxl file
def addConnection(connection_list, connection_appearance_list, connection_id, from_id, to_id):
  # Connection list
  newConnection = ElementTree.Element("connection", attrib={'connection': connection_id, 'from-id': from_id, 'to-id': to_id})
  connection_list.append(newConnection)
  
  newConnectionAppearance = ElementTree.Element("connection-appearance", attrib={"from-pos":"center", "to-pos":"center", "arrowhead":"if-to-concept"})
  connection_appearance_list.append(newConnectionAppearance)
  
# Indent function copied from stackoverflow to pretty print xml
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem        
  
def main():
  df = read_CSV("out1.csv")
  cxlFile = 'template.cxl'
  writeCXL(df, cxlFile)

if __name__ == "__main__":
  main()