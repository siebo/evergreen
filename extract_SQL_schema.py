# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 14:51:37 2018

@author: Andy Pham
SQL to CMAP Translation
"""
# STILL IN TESTING PHASE, TODO: TAKE OFF TESTING SCHEMA AND TRY IT WITH MULTIPLE SCHEMAS
import psycopg2 as pg
import pandas as pd
import create_cxl
import argparse

# INPUT: Connection object that is connected to the database instance
# OUTPUT: pandas dataframe representing SQL Schema columns, types, and table names
# Pulls out table names, constraints, and attributes and returns a dataframe with that information
def parseSchema(connection, schemaName):
  cur= connection.cursor()
  
  # Selecting attributes that do not have constraints
  queryAttributes = """
  SELECT ic.table_catalog, ic.table_schema, ic.table_name, ic.column_name
  FROM information_schema.columns as ic
  WHERE ic.table_schema = %s AND
  NOT EXISTS (SELECT ic.column_name FROM information_schema.key_column_usage as kcu WHERE kcu.column_name = ic.column_name) AND ic.table_schema NOT LIKE 'information_schema' AND ic.table_schema NOT LIKE 'pg_catalog'
  """ # MAKE SURE TO REMOVE TABLE NAME SELECTION AT THE END ^
  cur.execute(queryAttributes,(schemaName,))
  rows=cur.fetchall()
  schemaInfoDF = pd.DataFrame(rows, columns=['Database', 'Schema', 'Table_Name', 'Column_Name'])
  schemaInfoDF['Type'] = "attribute"
  
  # SELECTING other constraints (primary keys and unique)
  queryConstraints = """
  SELECT tc.constraint_catalog, tc.table_schema, tc.table_name, kcu.column_name, constraint_type 
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
  JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
  WHERE constraint_type NOT LIKE 'FOREIGN KEY' AND tc.table_schema = %s
  """ 
  cur.execute(queryConstraints, (schemaName,))
  rowsConstraints = cur.fetchall()
  schemaInfoDFConstraints = pd.DataFrame(rowsConstraints, columns=['Database', 'Schema', 'Table_Name', 'Column_Name', 'Type'])
  
  # SELECTING FOREIGN KEYS
  queryForeign = """
  SELECT tc.constraint_catalog, tc.table_schema, constraint_type, tc.table_name, ccu.table_name
  AS foreign_table_name, kcu.column_name,  ccu.column_name AS foreign_column_name
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
  JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
  WHERE constraint_type = 'FOREIGN KEY' and tc.table_schema = %s
  """
  
  cur.execute(queryForeign,(schemaName,))
  rowsForeign = cur.fetchall()

  # Foreign key attributes have a special format to denote table and column they're connected to
  foreignKeyList = list()
  for fk in rowsForeign:
    foreignKeyType = "foreign key::" + fk[4] + "::" + fk[6]
    foreignKeyList.append((fk[0], fk[1], fk[3], fk[5], foreignKeyType))
  schemaInfoDF_Foreign = pd.DataFrame(foreignKeyList, columns=['Database', 'Schema', 'Table_Name', 'Column_Name', 'Type'])
  
  # Connect all dataframes together into one large dataframe and create IDs for each concept
  sqlSchemaDF = pd.concat([schemaInfoDF, schemaInfoDF_Foreign, schemaInfoDFConstraints])
  sqlSchemaDF["ID"] = sqlSchemaDF.apply(lambda row: create_cxl.createCmapID(), axis=1)
  
  return sqlSchemaDF
  
  
def main():
  parser = argparse.ArgumentParser(description="Converts all SQl Schema layouts from a user-specified Postgres database into a formatted csv.")
  parser.add_argument("db", help="Database name from the server you are accessing.")
  parser.add_argument("--user", default="postgres", help="Username for the server you are accessing. (Default is postgres)")
  parser.add_argument("--host", default="localhost", help="Host-name/address for the server. (Default is localhost)" )
  parser.add_argument("--password")
  parser.add_argument("--output", default="out1.csv", help="File name for the output, make sure it ends with .csv (Default is out1.csv)")
  
  db_Parameters = parser.parse_args()
  conn = pg.connect(database=db_Parameters.db, user=db_Parameters.user, password="megawish", host=db_Parameters.host)
  sqlSchemaDF = parseSchema(conn, 'Lecture5')
  conn.close()
  sqlSchemaDF.to_csv(db_Parameters.output, index=False)

# To prevent imported module from running automatically
if __name__ == "__main__":
  main()