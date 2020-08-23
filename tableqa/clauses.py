
from tensorflow.keras.models import load_model
from sentence_transformers import SentenceTransformer
from numpy import asarray


class Clause:
    def __init__(self):
        self.bert_model = SentenceTransformer('bert-base-nli-mean-tokens')
        self.model=load_model("Question_Classifier.h5")
        self.types={0:'SELECT {} FROM {}', 1:'SELECT MAX({}) FROM {}', 2:'SELECT MIN({}) FROM {}', 3:'SELECT COUNT({}) FROM {}', 4:'SELECT SUM({}) FROM {}', 5:'SELECT AVG({}) FROM {}'}

    def adapt(self,q,inttype=False,priority=False):
        emb=asarray(self.bert_model.encode(q))
        self.clause=self.types[self.model.predict_classes(emb)[0]]
        
        if priority and inttype  and "COUNT" in self.clause:
            self.clause= '''SELECT SUM({}) FROM {}'''
        return self.clause
    
    


                
                

            

