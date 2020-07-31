import pandas as pd
import numpy as np
from pandas.io.sql import SQLTable
import mysql.connector
from sqlalchemy import create_engine, types
import subprocess
import os
import ast
from config import db_name
import column_types


def csv2sql(data_frame, schema, output_path):
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd=""
    )
    mycursor = mydb.cursor()
    try:
        mycursor.execute("CREATE DATABASE " + db_name)
        print('Database created: ' + db_name)
    except:
        pass
    engine = create_engine("mysql+mysqldb://root:@localhost/" + db_name)
    con = engine.raw_connection()
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
    con.commit()
    print("Dumping Table",schema["name"])
    os.system("mysqldump -u root  " + db_name + " > " + output_path)

def drop_db():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      passwd=""
    )
    mycursor = mydb.cursor()
    mycursor.execute("DROP DATABASE IF EXISTS "+db_name)
    