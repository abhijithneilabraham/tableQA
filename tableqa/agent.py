

import os
import nltk
from sqlalchemy import create_engine,types
import ast
from .column_types import get
from .data_utils import data_utils
from .nlp import Nlp
from .database import Database

class Agent:
    def __init__(self,data_dir,schema_dir=None,db_type='sqlite'):
        self.data_dir=data_dir
        self.schema_dir=schema_dir
        self.db_type=db_type
    def get_query(self,question):
        nlp=Nlp(self.data_dir,self.schema_dir)
        csv = nlp.csv_select(question)
        if csv is None:
            print("Sorry,didn't catch that")  
        else:
            question, valmap = nlp.get_sql_query(csv, question)
            sql_query=question
            for k, v in valmap.items():
                sql_query = sql_query.replace(k, v)
            print('SQL query:',sql_query)
            return sql_query
        
    def query_db(self,question):
        query=self.get_query(question)
        database=Database(self.data_dir,self.schema_dir) 
        create_db=getattr(database, self.db_type)
        engine=create_db(question)
        return engine.execute(query).fetchall()
 

