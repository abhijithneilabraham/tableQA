import os
import json
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet 
from nltk.stem import PorterStemmer 
ps = PorterStemmer().stem 
syns = wordnet.synsets
stop_words = list(set(stopwords.words('english')))
class data_utils:
    def __init__(self,data_dir,schema_dir):
        self.data_dir = data_dir
        self.schema_dir = schema_dir
        self.vocabfile=os.path.join(os.path.abspath(os.getcwd()),"vocab.json")
        self.valuesfile = os.path.join(os.path.abspath(os.getcwd()),"values.json")
    
    def get_csvs(self):
        ret = []
        for r, _, files in os.walk(self.data_dir):
            for f in files:
                if f.lower().endswith('.csv'):
                    ret.append(os.path.join(r, f))
        return ret
    
    
    def get_dataframe(self,csv_path):
        return pd.read_csv(csv_path)
       
    
    def get_schema_for_csv(self,csv_path):
        data=self.get_dataframe(csv_path)
        columns=data.columns.tolist()    
        if "unnamed" in columns[0].lower():
            columns[0]="index"
        data.columns=columns   
        try:
            with open(os.path.join(self.schema_dir, csv_path[len(self.data_dir) + 1:-4]) + '.json', 'r') as f:
                schema=json.load(f)
                schema_keywords=[]
                if "columns" not in schema.keys():
                    schema["columns"]=[]
                if "keywords" not in schema.keys():
                    for name in schema["name"].split("_"):
                        schema_syns=syns(ps(name))
                        schema_keywords.extend(list(set([i.lemmas()[0].name().lower().replace("_"," ") for i in  schema_syns])))
            
                if schema_keywords:
                    schema_keywords=[i for i in schema_keywords if i not in stop_words]
                    schema["keywords"]=schema_keywords
                
        except Exception as e:
            schema={}
            csvname=os.path.splitext(os.path.basename(csv_path))[0]
            schemaname=""
            for i in csvname.lower():
                if i.isalnum():
                    schemaname+=i
                else:
                    if not schemaname[-1]=="_":
                        schemaname+="_"
                
                    
            schema["name"]=schemaname
                
            schema_keywords=[]
            for name in schema["name"].split("_"):
                schema_syns=syns(ps(name))
                schema_keywords.extend(list(set([i.lemmas()[0].name().lower().replace("_"," ") for i in  schema_syns])))
            if schema_keywords:
                schema_keywords=[i for i in schema_keywords if i not in stop_words]
                schema["keywords"]=schema_keywords
                
            categorical_maps={i:list(set(data[i].dropna())) for i in data.columns if len(list(set(data[i].dropna())))==2}
            cat_kwd_maps={i:0 for i in categorical_maps}
            for k,v in categorical_maps.items():
                cat1syn,cat2syn=syns(ps(v[0])),syns(ps(v[1]))
                cat1=list(set([i.lemmas()[0].name().lower() for i in  cat1syn]))
                cat2=list(set([i.lemmas()[0].name().lower() for i in  cat2syn]))
                if not cat1:
                    cat1=[v[0]]
                if not cat2:
                    cat2=[v[1]]
                mapped_column={v[0]:cat1,v[1]:cat2}
                cat_kwd_maps[k]=mapped_column
                
            schema["columns"]=[]
            for column in columns:
                
                if column in categorical_maps:
                    schema["columns"].append({"name":column,"mapping":cat_kwd_maps[column]})
                else:
                    schema["columns"].append({"name":column})
                    
        finally:
            types=data.dtypes.apply(lambda x:x.name).to_dict()
            
            for k,v in types.items():
                if 'int' in v:
                    types[k]="Integer"
                if 'float' in v:
                    types[k]="Decimal"
                if "age" in k.lower():
                        types[k]="Age"
                if "year" in k.lower():
                        types[k]="Year"        
                if 'object' in v:
                    for col in schema["columns"]:
                        if "mapping" in col:
                            types[col["name"]]="Categorical"
                        else:
                            types[k]="FuzzyString"
                            
                collist=[]          
                for col in schema["columns"]:
                    collist.append(col["name"])
                    col["type"]=types[col["name"]]
                
                for column in columns:
                    if column not in collist:
                        schema["columns"].append({"name":column,"type":types[column],"keywords":[" ".join(column.lower().split('_'))]})
            return schema
            
    
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
    
             
    
    
        
    def create_values(self):
        self.del_vocab()
        values = {}
        for csv in self.get_csvs():
            df = self.get_dataframe(csv)
            schema = self.get_schema_for_csv(csv)
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
        
    
    

    
             
        




