

from .nlp import Nlp
from .database import Database
from .data_utils import Hide_logs
import pandas as pd

class Agent:
    """
    Generates sql queries and fetches query results from database.
    """
    def __init__(self,data_dir,schema_dir=None,db_type='sqlite'):
        """
        # Arguments

        data_dir: `str` or `pathlib.Path` object, absolute path to folder containing all input files.
        schema_dir: `str` or `pathlib.Path` object, path to folder containing `json` schemas of input files.
                    If not specified, auto-generated schema will be used.
        db_type: `str`, defining the type of Database object to be used.
                If not specified, default object is `sqlite`.
        """
        self.data_dir=data_dir
        self.schema_dir=schema_dir
        self.db_type=db_type

    def get_sql(self, question, nlp, df):
        question, valmap = nlp.get_sql_query(df, question)
        sql_query = question
        for k, v in valmap.items():
            sql_query = sql_query.replace(k, v)
        return sql_query

        

    def get_query(self, question, verbose=False):
        """
        # Arguments

        question: `str`,containing input utterance.
        verbose: `boolean`, Default False

        # Returns

        Returns a  `str` of generated sql query.
        """
        nlp = Nlp(self.data_dir, self.schema_dir)
        if isinstance(self.data_dir,pd.DataFrame):
            df=self.data_dir
        else:
            df = nlp.csv_select(question)
        if df is None:
            print("Sorry,didn't catch that")
        else:
            if verbose:
                sql_query = self.get_sql(question, nlp, df)
                print('SQL query:', sql_query)
                return sql_query
            else:
                with Hide_logs():
                    sql_query = self.get_sql(question, nlp, df)
                    return sql_query

    def query_db(self, question, verbose=False):
        """
        # Arguments

        question: `str`,containing input utterance.
        verbose: `boolean`, Default False

        # Returns

        Returns a  `list` of 'tuple` of query outputs from Database.
        """
        query = self.get_query(question,verbose)
        database = Database(self.data_dir, self.schema_dir)
        create_db = getattr(database, self.db_type)
        engine = create_db(question)
        return engine.execute(query).fetchall()
       

