

from sqlalchemy import create_engine,types
from sqlalchemy_utils import database_exists,create_database,drop_database
from sqlalchemy.exc import DatabaseError
from sqlalchemy.schema import DropTable
import awswrangler as wr
import ast
import pandas as pd
from .column_types import get
from .data_utils import data_utils
from .nlp import Nlp


class Database:
    def __init__(self,data_dir,schema_dir,aws_s3,access_key_id, secret_access_key):
        self.data_dir=data_dir
        self.schema_dir=schema_dir
        self.data_process=data_utils(data_dir,schema_dir,aws_s3,access_key_id, secret_access_key)
        self.nlp=Nlp(data_dir,schema_dir,aws_s3,access_key_id, secret_access_key)

    def fetch_data(self, question, query, db_type, username='', password='', database='', host='', port='', drop_db=True):
        # dialect+driver://username:password@host:port/database
        if db_type == 'sqlite':
            DB_URL = 'sqlite://'
        elif db_type == 'mysql':
            if port is None:    port = 3306     # use default port for mysql if it is None.
            DB_URL = 'mysql+pymysql://'+username+':'+password+'@'+host+':'+str(port)+'/'+database
        elif db_type == 'postgres':
            if port is None:    port = 5432     # use default port for postgres if it is None.
            DB_URL = 'postgres://'+username+':'+password+'@'+host+':'+str(port)+'/'+database
        engine = self.create_db(DB_URL)

        if isinstance(self.data_dir,pd.DataFrame):
            data_frame=self.data_dir
            schema=self.data_process.get_schema_for_csv(data_frame)
        else:
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

        # fetch the answer from the database.
        answer = engine.execute(query).fetchall()
        if db_type != 'sqlite':
            # drop the tables.
            self.delete_table(schema['name'].lower())
            # drop the database.
            if drop_db:    self.drop_db(DB_URL)

        return answer

    def create_db(self, db_url):
        # create database if it doesn't exists.
        try:
            engine = create_engine(db_url, echo=False)
            if not database_exists(engine.url):
                create_database(engine.url)
        except DatabaseError as e:
            import traceback
            traceback.print_exc()
            raise Exception("Check whether the server is running and the connection parameters are correct.")        
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception("Some error occured while connecting to the database.")
        return engine

    def drop_db(self, db_url):
        drop_database(db_url)

    def delete_table(self, table_name):
        DropTable(table_name)

    # Function to load and fetch data from AWS storage.
    def fetch_data_aws(self, question, query, db_type, username='', password='', database='', host='', port='', drop_db=True):
        # dialect+driver://username:password@host:port/database
        if db_type == 'postgres':
            if port is None:    port = 5432     # use default port for postgres if it is None.
            engine = wr.db.get_engine(db_type="postgresql", host=host, port=port, database=database, user=username, password=password)
            # engine =wr.catalog.get_engine("aws-postgres-sql", db_type="postgresql", host=host, port=port, database=database, user=username, password=password)
        elif db_type == 'mysql':
            if port is None:    port = 3306     # use default port for mysql if it is None.
            engine = wr.db.get_engine(db_type="mysql", host=host, port=port, database=database, user=username, password=password)

        if isinstance(self.data_dir,pd.DataFrame):
            data_frame=self.data_dir
            schema=self.data_process.get_schema_for_csv(data_frame)
        else:
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

        wr.db.to_sql(data_frame, engine, name=schema['name'].lower(), if_exists="replace", dtype=sql_schema, index=False) 

        # fetch the answer from the database.
        answer = wr.db.read_sql_query(query, con=engine)
        answer = answer.values.tolist()

        # delete the database
        # wr.catalog.delete_table_if_exists(database=database, table=schema['name'].lower())  # deleted

        return answer