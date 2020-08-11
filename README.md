# tableQA
Tool for querying natural language on tabular data like csvs,excel sheet,etc.   


### Configuration:
      Point the 'data_dir' and 'schema_dir' variables in config.py to path consisting of csv files and respective schemas.   

      
## Quickstart


```
cd tableqa
```

```
import agent
print(agent.get_response("how many people died of stomach cancer in 2011")) #returns an sql query
```

To do an example query on sqlite database
```
import test
print(test.csv2sql("how many people died of stomach cancer in 2011")) #returns the count 
```
