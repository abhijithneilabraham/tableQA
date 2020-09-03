

import pandas as pd
import numpy as np
from numpy import asarray
from nltk.tokenize import sent_tokenize
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Lambda, Flatten
from tensorflow.keras.models import Sequential, load_model, model_from_config
from tensorflow.keras.layers import Dense, Flatten, LSTM, Conv1D, MaxPooling1D, Dropout, Activation
import tensorflow as tf
from transformers import DistilBertTokenizer, TFDistilBertModel

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
bert_model = TFDistilBertModel.from_pretrained('distilbert-base-uncased')
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


# bert_model = SentenceTransformer('average_word_embeddings_glove.6B.300d')
def get_bert_embeddings(x):
    emb=[]
    for i,sentence in enumerate(x):
        print(i)
        input_ids = tf.constant(tokenizer.encode(sentence))[None, :]  # Batch size 1
        outputs = bert_model(input_ids)
        last_hidden_states = outputs[0][0][1] 
        emb.append(last_hidden_states)
    return asarray(emb)
train_embeddings =get_bert_embeddings(x_train.tolist())
test_embeddings = get_bert_embeddings(x_test.tolist())
y_train=asarray(y_train,dtype="float32")
y_test=asarray(y_test,dtype="float32")

model = get_keras_model()
print(train_embeddings.shape)
model.fit(train_embeddings, y_train, epochs=200,validation_data=(test_embeddings,y_test))

model.save("Question_Classifier_Bert.h5")



        

    



    

