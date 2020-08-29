from nlp import qa
import tensorflow as tf

class Clause:
    def __init__(self):
        
        self.base_q="what is {} here"
        self.types={"the entity":'SELECT {} FROM {}', "the maximum":'SELECT MAX({}) FROM {}', "the minimum":'SELECT MIN({}) FROM {}', "counted":'SELECT COUNT({}) FROM {}', "summed":'SELECT SUM({}) FROM {}', "averaged":'SELECT AVG({}) FROM {}'}

    def adapt(self,q,inttype=False,priority=False):
        scores={}
        validated_scores={}
        total_scores={}
        for k,v in self.types.items():
            scores[k]=tf.convert_to_tensor(qa(q,self.base_q.format(k),return_score=True)[1])
        return self.types[max(scores, key=scores.get)]
            
            