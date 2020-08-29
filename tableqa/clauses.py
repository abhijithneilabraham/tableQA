
#from nlp import qa
# class Clause:
#     def __init__(self):
        
#         self.base_q="what is {} here"
#         self.types={"the entity":'SELECT {} FROM {}', "the maximum":'SELECT MAX({}) FROM {}', "the minimum":'SELECT MIN({}) FROM {}', "counted":'SELECT COUNT({}) FROM {}', "summed":'SELECT SUM({}) FROM {}', "averaged":'SELECT AVG({}) FROM {}'}

#     def adapt(self,q,inttype=False,priority=False):
#         scores={}
#         for k,v in self.types.items():
#             scores[k]=qa(q,self.base_q.format(k),return_score=True)[1]
#         return self.types[max(scores, key=scores.get)]
            
            