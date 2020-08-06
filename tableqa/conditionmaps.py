#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:24:35 2020

@author: abhijithneilabraham
"""


conditions={
  "<":["below","lower","lesser","smaller"],
  ">":["above","higher","greater","bigger"]
}

import re
print(re.sub("'"+"<","","'> 20'"))