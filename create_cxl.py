import pandas as pd
import argparse
from xml.etree import ElementTree
from string import ascii_uppercase
from string import digits
from random import SystemRandom


ElementTree.register_namespace('', "http://cmap.ihmc.us/xml/cmap/")
ElementTree.register_namespace('dcterms', "http://purl.org/dc/terms/")
ElementTree.register_namespace('dc', "http://purl.org/dc/elements/1.1/")
ElementTree.register_namespace('vcard', "http://www.w3.org/2001/vcard-rdf/3.0#")

# TESTING PHASE

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

# ETL from dataframe to cxl file format
# INPUT: pandas dataframe, string schema name, and path to cxl file
def writeCXL(df_SQL, schemaName, cxl):
  
  # Open the blank CXL template
  e = ElementTree.parse('template.cxl')
  root = e.getroot()
  
  # root [0][0] corresponds to res-meta tag
  # root [1][0] corresponds to concept-list tag  
  concept_list = root[1][0] # For table names and column names
  linking_list = root[1][1] # For relationships between the tables and columns
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
  df_LinkingPhraseInfo = pd.DataFrame(columns=["Linking_Phrase", "Linking_Phrase_ID", "Table_Name"])
  
  # For foreign key connections to other columns
  df_ReferenceInfo = pd.DataFrame(columns=["Reference_ID", "To"])
  
  # Processing tables and writing to cxl file at the same time
  # Write first to cxl, then process values into tables for later lookup
  for table in tableDict:
    addConcepts(concept_list, concept_appearance_list, "concept", {'id': tableDict[table], 'label': table})
    df_TableName = df_SQL[df_SQL.loc[:, "Table_Name"] == table]
    
    # Go through each row in the table containing column info to put in connections and linking phrases one by one
    for row in df_TableName.itertuples():
      addConcepts(concept_list, concept_appearance_list, "concept", {'id': row.ID, 'label': row.Column_Name})
      
      # Isolating linking phrases by table name for simplicity        
      df_LinkingPhraseSubset = df_LinkingPhraseInfo[df_LinkingPhraseInfo.Table_Name == table]
      
      # To match cmap terminology
      if "foreign key" in row.Type:
        linkingPhraseLabel = "has FOREIGN KEY"
      else:
        linkingPhraseLabel = "has " + row.Type
      
      # If there is a linking phrase for "has attribute" that exists for the table, retrieve it
      if df_LinkingPhraseSubset[df_LinkingPhraseSubset.Linking_Phrase == linkingPhraseLabel].shape[0] > 0:
        linkingPhraseLocation = df_LinkingPhraseSubset[df_LinkingPhraseSubset.Linking_Phrase == linkingPhraseLabel].index.tolist()
        
        # Append to connection list, connecting concept -> linking phrase -> concept using two connections
        addConnection(connection_list, connection_appearance_list, createCmapID(), tableDict[table], df_LinkingPhraseSubset.at[linkingPhraseLocation[0], "Linking_Phrase_ID"])
        addConnection(connection_list, connection_appearance_list, createCmapID(), df_LinkingPhraseSubset.at[linkingPhraseLocation[0], "Linking_Phrase_ID"], row.ID)
          
          
      # Else add the linking phrase to the dataframe for lookup and add linking phrase to the cxl file
      else:
        linkingPhraseID = createCmapID()
        df_LinkingPhraseInfo.loc[df_LinkingPhraseInfo.shape[0]] = [linkingPhraseLabel, linkingPhraseID, table]
        addConcepts(linking_list, linking_appearance_list, "linking-phrase", {'id': linkingPhraseID, 'label': linkingPhraseLabel})
        
        # Append to connection list, connecting concept -> linking phrase -> concept using two connections
        addConnection(connection_list, connection_appearance_list, createCmapID(), tableDict[table], linkingPhraseID)
        addConnection(connection_list, connection_appearance_list, createCmapID(), linkingPhraseID, row.ID)
       
  
  # Connect Foreign keys
  df_ForeignKey = df_SQL[df_SQL["Type"].str.contains('foreign key')]
  foreignKeyLabel = "REFERENCES"
  for foreign_row in df_ForeignKey.itertuples():
    foreignTable = foreign_row.Type.split("::")[1]
    foreignColumn = foreign_row.Type.split("::")[2]
    localColumnID = foreign_row.ID
    
    # Find foreign column using table name and column name -> get column id -> form connection using references
    df_foreignColumn = df_SQL[(df_SQL.Table_Name == foreignTable) & (df_SQL.Column_Name == foreignColumn)]
    foreignColumnIndex = df_foreignColumn.index.tolist()
    foreignColumnID = df_foreignColumn.at[foreignColumnIndex[0], "ID"]
    
    # Check to see if reference connection is already made
    referenceCheck = df_ReferenceInfo[df_ReferenceInfo.To == foreignColumnID]
    if referenceCheck.shape[0] > 0:
      referenceIndex = referenceCheck.index.tolist()
      referenceID = referenceCheck.at[referenceIndex[0], "Reference_ID"]
      
      # Add 1 connection from local column to linking reference phrase
      addConnection(connection_list, connection_appearance_list, createCmapID(), localColumnID, referenceID)
    
    # No reference made 
    else:
      new_ReferenceID = createCmapID()
      df_ReferenceInfo.loc[df_ReferenceInfo.shape[0]] = [new_ReferenceID, foreignColumnID]
      
      # Add to linking-phrase list
      addConcepts(linking_list, linking_appearance_list, "linking-phrase", {'id': new_ReferenceID, 'label': foreignKeyLabel})
      
      # Add 2 connections for new references
      addConnection(connection_list, connection_appearance_list, createCmapID(), localColumnID, new_ReferenceID)
      addConnection(connection_list, connection_appearance_list, createCmapID(), new_ReferenceID, foreignColumnID)
      
  # Formatting CXL file and writing  
  indent(root)
  fileName = schemaName + '.cxl'
  e.write(fileName)      
 
# Adds formatted XML elements for the concepts and appearances portions of cxl file
# INPUT: XML filepath parser for concept, an XML filepath parser for the appearance, a string representing the concept, a dictionary with attributes for the element
def addConcepts(concept_list, concept_appearance_list, name, attribute_list):
  # Concept element appending
  newConcept = ElementTree.Element(name, attrib=attribute_list)
  appearance_Name = name + "-appearance"
  newAppearance = ElementTree.Element(appearance_Name, attrib={'id': attribute_list['id'], "x":"0", "y":"0", "width":"80", "height":"25"})
  
  # Writing concept to cxl
  concept_list.append(newConcept)
  concept_appearance_list.append(newAppearance)

# Adds connection and connection appearance elements to make links for the cxl file
def addConnection(connection_list, connection_appearance_list, connection_id, from_id, to_id):
  # Connection element appending
  newConnection = ElementTree.Element("connection", attrib={'connection': connection_id, 'from-id': from_id, 'to-id': to_id})
  newConnectionAppearance = ElementTree.Element("connection-appearance", attrib={"from-pos":"center", "to-pos":"center", "arrowhead":"if-to-concept"})
  
  # Writing connections to cxl
  connection_list.append(newConnection)
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
  
  # Read command-line arguments
  parser = argparse.ArgumentParser(description="Takes in a csv and converts it to CXL for concept mapping.")
  parser.add_argument("--input", default="out1.csv", help="Input file in csv format for conversion.  (Default is out1.csv)")
  
  cxl_Parameters = parser.parse_args()
  
  # Load csv into dataframe for processing
  df = read_CSV(cxl_Parameters.input)
  cxlFile = 'template.cxl'
  
  # Separate each cxl file by schema
  for schema in df.Schema.unique():
    df_Schema = df[df.Schema == schema]
    writeCXL(df_Schema, schema, cxlFile)

if __name__ == "__main__":
  main()