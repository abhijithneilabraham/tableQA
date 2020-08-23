# tableQA
Tool for querying natural language on tabular data like csvs,excel sheet,etc.   

#### Features    
* Supports detection from multiple csvs 
* Support FuzzyString implementation. i.e, incomplete csv values in query can be automatically detected and filled.
* Open-Domain, No training required.


### Configuration:
```git clone https://github.com/abhijithneilabraham/tableQA ```  

```cd tableqa```

```pip install -r requirements.txt```

      
## Quickstart

Keep the csv data and the schemas in seperate folders. Refer ```cleaned_data``` and `schema` for dummy datas.

#### Getting an SQL query from csv 

```
from agent import Agent
agent=Agent(data_dir,schema_dir) #specify the data and schema directories.
print(agent.get_response("Your question here")) #returns an sql query
```

#### Do Sample query on sqlite database
```
from database import Database
database=Database(data_dir, schema_dir)
response=database.Query_Sqlite("Your question here")
print("Response ={}".format(response)) #returns the result of the sql query after feeding the csv to the database
```
