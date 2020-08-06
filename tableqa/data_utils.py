import os
import json
import pandas as pd
import nltk
from nltk.corpus import stopwords
import sys

data_dir = 'cleaned_data'
schema_dir = 'schema'
vocabfile='vocab.json'
def get_csvs():
    ret = []
    for r, _, files in os.walk(data_dir):
        for f in files:
            if f.lower().endswith('.csv'):
                ret.append(os.path.join(r, f))
    return ret


def get_schema_for_csv(csv_path):
    try:
        with open(os.path.join('schema', csv_path[len(data_dir) + 1:-4]) + '.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None


def get_dataframe(csv_path):
    return pd.read_csv(csv_path)

def write_columns(txt_path,df):
    for colname in df.columns:
        if df[colname].dtype==object:
            col=set(df[colname].dropna(axis=0).tolist())         
            try:
                with open(os.path.join(txt_path,colname+'.txt'),'w+') as f:   
                    for i in col:
                        f.write(i+"\n")
            except Exception as e:
                continue
    

def csv_keyword_vocab(csvname,schema):
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
    if os.path.exists(vocabfile):

        with open(vocabfile, "r+") as file: 
            data=json.load(file)
            data.update(mapped_kwds)
            file.seek(0)
            json.dump(data, file)
    else:
        json_object = json.dumps(mapped_kwds) 
        with open(vocabfile, "w") as file: 
            file.write(json_object)
    

def kwd_checker(csv,vocab):
    vocablist=[]
    for k,v in vocab.items():
        if not k==csv:
            vocablist.extend(v)
    return vocablist



            
        
    
         
def del_vocab():
    if os.path.isfile(vocabfile):
        os.remove(vocabfile)



    



    

         
    




