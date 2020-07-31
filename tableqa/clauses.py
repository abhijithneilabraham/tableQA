#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 18:47:53 2020

@author: abhijithneilabraham
"""

class Clause:
    def __init__(self):
        self.clauses={
                      ("find","search for","what","get me","which","show"):"select {} in {}",
                      ("how many","number of","who all","how much","sum of","total"):"count {} in {}",
                      ("instances","count"):"count {} in {}",
                      ("max","maximum","highest","biggest","most"):"maximum of {} in {}",
                      ("min","minimum","lowest","smallest","least"):"minimum of {} in {}",
                      ("average","mean of"):"average of {} in {}"
                      }
        self.int_clauses={v[0]:v[1] for i,v in enumerate(self.clauses.items()) if i>2}
    def adapt(self,q,inttype=False,priority=False):
        clauses=self.clauses
        int_clauses=self.int_clauses

        for i,tup in enumerate(clauses.items()):
            clause=tup[0]
            if any(i in q for i in clause):
                if priority and inttype  and "how many" in clause:
                    return "sum of {} in {}"
                elif "which" in clause and inttype:
                    for clause2 in int_clauses:
                        if any(i in q for i in clause2):
                            return int_clauses[clause2]
                    return clauses[clause]
                else:
                    return clauses[clause]
            

