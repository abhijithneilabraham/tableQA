

from sqlalchemy import create_engine,types
import ast
from .agent import Agent
from .column_types import get
from .data_utils import data_utils
from .nlp import Nlp


class Database:
    def __init__(self,data_dir,*args,**kwargs):
        if args:
            self.schema_dir=args[0]
        else:
            self.schema_dir=None
        self.data_dir=data_dir
        self.data_process=data_utils(data_dir, self.schema_dir)
        self.nlp=Nlp(data_dir,self.schema_dir)
    def Query_Sqlite(self,question):
        agent=Agent(self.data_dir,self.schema_dir)
        query=agent.get_response(question)   
        print("sql query: {}".format(query))
        engine = create_engine('sqlite://', echo=False)
        csv=self.nlp.csv_select(question)
        data_frame=self.data_process.get_dataframe(csv).astype(str)
        schema=self.data_process.get_schema_for_csv(csv)   
        data_frame = data_frame.fillna(data_frame.mean())
        sql_schema = {}
        for col in schema['columns']:
            colname = col['name']
            coltype = col['type']
            coltype = get(coltype).sql_type
            if '(' in coltype:
                coltype, arg = coltype.split('(')
                arg ='(' + arg[:-1] + ',)'
                coltype = getattr(types, coltype)(*(ast.literal_eval(arg)))
            else:
                coltype = getattr(types, coltype)()
            sql_schema[colname] = coltype
        data_frame.to_sql(schema['name'].lower(), con=engine, if_exists='replace', dtype=sql_schema)

        return engine.execute(query).fetchall()




    


    



