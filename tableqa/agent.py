from nlp import Nlp
from data_utils import data_utils
import os

filepath = os.path.dirname(__file__)
class Agent:
    def __init__(self,data_dir,schema_dir):
        self.data_dir=data_dir
        self.schema_dir=schema_dir
        
    
    def get_response(self,question):
        try:
            data_process=data_utils(self.data_dir,self.schema_dir)
            data_process.create_vocab()
            nlp=Nlp(self.data_dir,self.schema_dir)
            csv = nlp.csv_select(question)
            if csv is None:
                print("Sorry,didn't catch that")    
            question, valmap = nlp.get_sql_query(csv, question)

            sql_query=question
            for k, v in valmap.items():
                sql_query = sql_query.replace(k, v)
            
            return sql_query
        except Exception as e:
                print(e)
          
