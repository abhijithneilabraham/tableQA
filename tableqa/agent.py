

from .nlp import Nlp
from .database import Database

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
    def get_query(self,question):
        """
        # Arguments
        
        question: `str`,containing input utterance.
        
        # Returns
        
        Returns a  `str` of generated sql query.
        """
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
        """
        # Arguments
        
        question: `str`,containing input utterance.
        
        # Returns
        
        Returns a  `list` of 'tuple` of query outputs from Database.
        """
        query=self.get_query(question)
        database=Database(self.data_dir,self.schema_dir) 
        create_db=getattr(database, self.db_type)
        engine=create_db(question)
        return engine.execute(query).fetchall()
 

