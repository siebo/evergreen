# SQL-TO-CMAP PIPELINE
## DESCRIPTION
Using two scripts, convert all the schemas in a given Postgresql database into concept map format through CXL conversion.

## RUNNING THE SCRIPTS

### Loading the PostgreSQL Database into CSV file
First clone the github repository into your local computer.
Then run the script `extract_SQL_schema.py`

```
extract_SQL_schema.py mydatabasename 
```

`mydatabasename` is the name of the database you want to access. Any further details can be queried using `extract_SQL_schema.py -h` 


### Converting the CSV File into CXL

After running the above script, run `create_cxl.py`

```
create_cxl.py
```

Any further details can be queried using `create_cxl.py -h`. Once the script is done running, there is a separate cxl file for each schema, with the name of the files corresponding to the respective schema.

### Opening the CXL files on CMAP

Open CmapTools, click on `File -> Import -> Cmap from CXL File...`
Once the file is loaded, the concepts and linking phrases are **not formatted** so you will have to either type `Ctrl-L` or go to `Format -> AutoLayout` in order to see the entire schema. The recommended format is the horizontal layout. 

## DEPENDENCIES AND REQUIREMENTS
python>=3.5  
psycopg2>=2.7.4  
pandas>= 19.2  


