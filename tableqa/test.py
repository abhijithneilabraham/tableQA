#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 03:20:55 2020

@author: abhijithneilabraham
"""

from agent import get_response
import os
import sys
def test():
    if os.path.exists(os.path.join("test","log.txt")):
        os.remove("log.txt")
    with open(os.path.join("test","test_inputs.txt")) as f:
        questions=f.read().splitlines()
        for q in questions:
            sys.stdout = open(os.path.join("test","log.txt"), "a")
            print(q)
            print(get_response(q))
        sys.stdout.close()
if __name__ == '__main__':
    test()