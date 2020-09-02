

import os
import nltk

def _nltk_downloader():
    try:
        nltk.download('wordnet',quiet=True)
        nltk.download('averaged_perceptron_tagger',quiet=True)
    except LookupError as e:
        print(e)
_nltk_downloader()


from .nlp import Nlp
class Agent:
    def __init__(self,data_dir,*args,**kwargs):
        self.data_dir=data_dir
        if args:
            self.schema_dir=args[0]
        else:
            self.schema_dir=None
    def get_response(self,question):
        nlp=Nlp(self.data_dir,self.schema_dir)
        csv = nlp.csv_select(question)
        if csv is None:
            print("Sorry,didn't catch that")    
        question, valmap = nlp.get_sql_query(csv, question)
        sql_query=question
        for k, v in valmap.items():
            sql_query = sql_query.replace(k, v)
        
        return sql_query
 

