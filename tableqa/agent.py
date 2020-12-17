

from .nlp import Nlp
from .database import Database
from .data_utils import Hide_logs
import pandas as pd
from .chart import Chart

class Agent:
    """
    Generates sql queries and fetches query results from database.
    """
    def __init__(self,data_dir,schema_dir=None,db_type='sqlite',username='',password='',database='db',host='localhost',port=None,drop_db=True,aws_db=False, aws_s3=False, access_key_id="", secret_access_key=""):
        """
        # Arguments

        data_dir: `str` or `pathlib.Path` object, absolute path to folder containing all input files.
        schema_dir: `str` or `pathlib.Path` object, path to folder containing `json` schemas of input files.
                    If not specified, auto-generated schema will be used.
        db_type: `str`, defining the type of Database object to be used.
                If not specified, default object is `sqlite`.
        username: `str`, username for connecting to the database.
                (Optional) Not required for connectivity to sqlite.
        password: `str`, username for connecting to the database.
                (Optional) Not required for connectivity to sqlite.
        database: `str`, database name.
                (Optional) Not required for connectivity to sqlite.
        host:   `str`, address of the web server to be accessed.
                (Optional) Not required for sqlite connectivity.
        port:   `str`, number to identify a webserver at the provided hostname.
                (Optional) Not required for sqlite connectivity.
        drop_db:  `boolean`, Drop the database. (Optional, default=True)
        aws_db:   `boolean`, Connect to database on AWS. (Optional, default=False)
        aws_s3:   `boolean`, Connect to AWS s3. (Optional, default=False)
        access_key_id: `str`, Access key. (Optional, required for connecting to AWS s3)
        secret_access_key: `str`, Secret access key. (Optional, required for connecting to AWS s3)
        """
        self.data_dir=data_dir
        self.schema_dir=schema_dir
        self.db_type=db_type
        self.username=username
        self.password=password
        self.database=database
        self.host=host
        self.port=port
        self.drop_db=drop_db
        self.aws_db = aws_db
        self.aws_s3 = aws_s3
        self.access_key_id = access_key_id 
        self.secret_access_key = secret_access_key
        

    def get_query(self, question, verbose=False,distinct=False):
        """
        # Arguments

        question: `str`,containing input utterance.
        verbose: `boolean`, Default False
        distinct: `boolean`, to select distinct values from dataframe
        # Returns

        Returns a  `str` of generated sql query.
        """
        nlp = Nlp(self.data_dir, self.schema_dir, self.aws_s3, self.access_key_id, self.secret_access_key )
        if isinstance(self.data_dir,pd.DataFrame):
            df=self.data_dir
        else:
            df = nlp.csv_select(question)
        if df is None:
            print("Sorry,didn't catch that")
        else:
            if verbose:
                sql_query = nlp.get_sql_query(df, question,distinct=distinct)
                print('SQL query:', sql_query)
                return sql_query
            else:
                with Hide_logs():
                    sql_query = nlp.get_sql_query(df, question,distinct=distinct)
                    return sql_query

    def query_db(self, question, verbose=False, chart=None, size=(10, 10),distinct=False):
        """
        # Arguments

        question: `str`,containing input utterance.
        verbose: `boolean`, Default False
        chart: `str`, specify type of chart. Default None.
        size: `tuple`, figure size.
        distinct: `boolean`, to select distinct values from dataframe

        # Returns

        Returns a  `list` of 'tuple` of query outputs from Database.
        """
        query = self.get_query(question,verbose,distinct=distinct)
        database = Database(self.data_dir, self.schema_dir, self.aws_s3, self.access_key_id, self.secret_access_key)
        if self.aws_db:
            fetch_data = getattr(database, 'fetch_data_aws')
        else:
            fetch_data = getattr(database, 'fetch_data')
        answer = fetch_data(question, query, self.db_type, self.username, self.password, self.database, self.host, self.port, self.drop_db)

        if chart is not None:
            Chart(chart, query, answer, size)
        return answer
       

