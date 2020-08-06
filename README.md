# tableQA
Tool for querying natural language on tabular data like csvs,excel sheet,etc.Takes input of a csv+schema and returns an sql query.

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
