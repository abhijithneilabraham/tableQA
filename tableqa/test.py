#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 22:23:02 2020

@author: abhijithneilabraham
"""

import agent
from sqlalchemy import create_engine,types
import column_types
import ast
from data_utils import get_dataframe,get_schema_for_csv
from nlp import csv_select

def csv2sql(question):
    engine = create_engine('sqlite://', echo=False)
    csv=csv_select(question)
    data_frame=get_dataframe(csv).astype(str)
    schema=get_schema_for_csv(csv)

    data_frame = data_frame.fillna(data_frame.mean())
    sql_schema = {}
    for col in schema['columns']:
        colname = col['name']
        coltype = col['type']
        coltype = column_types.get(coltype).sql_type
        if '(' in coltype:
            coltype, arg = coltype.split('(')
            arg ='(' + arg[:-1] + ',)'
            coltype = getattr(types, coltype)(*(ast.literal_eval(arg)))
        else:
            coltype = getattr(types, coltype)()
        sql_schema[colname] = coltype
    data_frame.to_sql(schema['name'].lower(), con=engine, if_exists='replace', dtype=sql_schema)
    query=agent.get_response(question)
    print(query)
  
    return engine.execute(query).fetchall()




    


    



