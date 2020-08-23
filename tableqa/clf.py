#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 22:30:11 2020

@author: abhijithneilabraham
"""

import pandas as pd
import numpy as np
from numpy import asarray
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Lambda, Flatten
from tensorflow.keras.models import Sequential, load_model, model_from_config
from tensorflow.keras.layers import Dense, Flatten, LSTM, Conv1D, MaxPooling1D, Dropout, Activation

np.random.seed(7)

def get_keras_model():
    """Define the model."""
    model = Sequential()
    model.add(Dense(512, input_shape=[768,], activation='relu'))
    model.add(Dense(128,activation='relu'))
    model.add(Dense(6, activation='softmax'))
    model.compile(loss = 'sparse_categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
    model.summary()
    return model

data=pd.read_csv("wikidata.csv",usecols=["questions","types"])

categories=data["types"]
#print(categories.tolist().count(0))


x_train, x_test, y_train,y_test =train_test_split(data["questions"],categories)

bert_model = SentenceTransformer('bert-base-nli-mean-tokens')
# bert_model = SentenceTransformer('average_word_embeddings_glove.6B.300d')

train_embeddings = asarray(bert_model.encode(x_train.tolist()), dtype = "float32")
test_embeddings = asarray(bert_model.encode(x_test.tolist()), dtype = "float32")
y_train=asarray(y_train,dtype="float32")
y_test=asarray(y_test,dtype="float32")

model = get_keras_model()
model.fit(train_embeddings, y_train, epochs=100,validation_data=(test_embeddings,y_test))

print('\n# Evaluate on test data')
results = model.evaluate(test_embeddings, y_test, batch_size=128)
print('test loss, test acc:', results)



model.save("Question_Classifier.h5")


        

    



    

