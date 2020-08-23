

from database import Database
database=Database("cleaned_data", "schema")
response=database.Query_Sqlite("how many people died of stomach cancer in 2011")
print("Response ={}".format(response))
    