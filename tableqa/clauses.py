import tensorflow as tf
from tensorflow.keras.models import load_model
from transformers import BertTokenizer, TFBertModel
from numpy import asarray
import os

class Clause:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = TFBertModel.from_pretrained('bert-base-uncased')
        self.model=load_model(os.path.join(os.path.abspath(os.path.dirname(__file__)),"Question_Classifier_Bert.h5"))
        self.types={0:'SELECT {} FROM {}', 1:'SELECT MAX({}) FROM {}', 2:'SELECT MIN({}) FROM {}', 3:'SELECT COUNT({}) FROM {}', 4:'SELECT SUM({}) FROM {}', 5:'SELECT AVG({}) FROM {}'}
    
    def get_bert_embeddings(self,x):
        emb=[]
        for i,sentence in enumerate(x):
            input_ids = tf.constant(self.tokenizer.encode(sentence))[None, :]  # Batch size 1
            outputs = self.bert_model(input_ids)
            last_hidden_states = outputs[0][0][1] 
            emb.append(last_hidden_states)
        return asarray(emb)

    def adapt(self,q,inttype=False,summable=False):
        emb=self.get_bert_embeddings([q])
        self.clause=self.types[self.model.predict_classes(emb)[0]]
        
        if summable and inttype  and "COUNT" in self.clause:
            self.clause= '''SELECT SUM({}) FROM {}'''
        return self.clause
    
    


                
                

            

