from nlp import get_sql_query,slot_fill,cond_map,clause_arrange,csv_select
from data_utils import get_dataframe,get_csvs, get_schema_for_csv
from config import db_name
import os
import json
import pandas as pd
import column_types
  
filepath = os.path.dirname(__file__)


def get_table(df):
    df = df.astype(str)[:1000]
    cols = [" ".join(i.split('_')) for i in df.columns]
    df.columns=cols
    table = {"columns":[{'title': col, 'key': col} for col in cols]}
    table["rows"] = df.to_dict(orient="records")
    return table

def get_response(question):

    try:
        csv = csv_select(question)
        if csv is None:
            print("Sorry,didn't catch that")
    
        schema = get_schema_for_csv(csv)
        question, valmap = clause_arrange(csv, question)
        if question[0] == ',':
            question = "Select None from " + schema['name'].lower().replace('_', ' ') + ' ' + question[1:]
        print(question)
        sql_query=get_sql_query(question)
        for k, v in valmap.items():
            sql_query = sql_query.replace(k, v)
       
        return sql_query
    except Exception as e:
            print(e)
          
