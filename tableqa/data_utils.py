import os
import json
import pandas as pd
import nltk
from nltk.corpus import stopwords
import sys
class data_utils:
    def __init__(self,data_dir,schema_dir):
        self.data_dir = data_dir
        self.schema_dir = schema_dir
        self.vocabfile='vocab.json'
        self.valuesfile = 'values.json'
    
    def get_csvs(self):
        ret = []
        for r, _, files in os.walk(self.data_dir):
            for f in files:
                if f.lower().endswith('.csv'):
                    ret.append(os.path.join(r, f))
        return ret
    
    
    def get_schema_for_csv(self,csv_path):
        try:
            with open(os.path.join(self.schema_dir, csv_path[len(self.data_dir) + 1:-4]) + '.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(e)
            return None
    
    
    def get_dataframe(self,csv_path):
        return pd.read_csv(csv_path)
    
    def write_columns(self,txt_path,df):
        for colname in df.columns:
            if df[colname].dtype==object:
                col=set(df[colname].dropna(axis=0).tolist())         
                try:
                    with open(os.path.join(txt_path,colname+'.txt'),'w+') as f:   
                        for i in col:
                            f.write(i+"\n")
                except Exception as e:
                    continue
        
    
    def csv_keyword_vocab(self,csvname,schema):
        vocab=[]
        if '_' in schema['name']:
            vocab.extend(schema['name'].split('_'))
        else:
            vocab.append(schema['name'])
        if 'keywords' in schema.keys():
            for word in schema['keywords']:
                vocab.extend(nltk.word_tokenize(word))
           
        for col in schema['columns']:
            
            if '_' in col['name']:
                vocab.extend(col['name'].split('_'))
            else:
                vocab.append(col['name'])
                
            if 'keywords' in col.keys():
                 for kwds in col['keywords']:
                     vocab.extend(nltk.word_tokenize(kwds))
        stop_words = set(stopwords.words('english'))
        vocab=[i.lower() for i in vocab if i.lower() not in stop_words]
        vocab=list(set(vocab))
        mapped_kwds={os.path.basename(csvname):vocab}
        if os.path.exists(self.vocabfile):
    
            with open(self.vocabfile, "r+") as file: 
                data=json.load(file)
                data.update(mapped_kwds)
                file.seek(0)
                json.dump(data, file)
        else:
            json_object = json.dumps(mapped_kwds) 
            with open(self.vocabfile, "w") as file: 
                file.write(json_object)
        
    
    def kwd_checker(self,csv,vocab):
        vocablist=[]
        for k,v in vocab.items():
            if not k==csv:
                vocablist.extend(v)
        return vocablist
    
    
    
                
            
            
    def del_vocab(self):
        if os.path.isfile(self.vocabfile):
            os.remove(self.vocabfile)
    
             
    
    
        
    def create_vocab(self):
        self.del_vocab()
        values = {}
        for csv in self.get_csvs():
            df = self.get_dataframe(csv)
            schema = self.get_schema_for_csv(csv)
            if schema is not None:
                self.csv_keyword_vocab(csv,schema)
                for col in schema['columns']:
                    if col['type'] == "FuzzyString":
                        colname = col['name']
                        if colname not in values:
                            values[colname] = []
                        vals = values[colname]
                        vals += list(set([x for x in df[colname] if isinstance(x, str)]))
        with open(self.valuesfile, 'w') as f:
            json.dump(values, f)
        
    
    

    
             
        




