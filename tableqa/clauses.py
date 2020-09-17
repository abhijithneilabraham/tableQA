
from tensorflow.keras.models import load_model
import tensorflow_hub as hub
from numpy import asarray,argmax
import os

embed = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
model=load_model(os.path.join(os.path.abspath(os.path.dirname(__file__)),"Question_Classifier.h5"))


class Clause:


    def __init__(self):
        self.types = {0: 'SELECT {} FROM {}', 1: 'SELECT MAX({}) FROM {}', 2: 'SELECT MIN({}) FROM {}',
                      3: 'SELECT COUNT({}) FROM {}', 4: 'SELECT SUM({}) FROM {}', 5: 'SELECT AVG({}) FROM {}'}

    def get_embeddings(self, x):
        embeddings = embed(x)
        return asarray(embeddings)

    def adapt(self, q, inttype=False, summable=False):
        emb = self.get_embeddings([q])
        self.clause = self.types[argmax(model.predict(emb))]

        if summable and inttype and "COUNT" in self.clause:
            self.clause = '''SELECT SUM({}) FROM {}'''
        return self.clause

    


                
                

            

