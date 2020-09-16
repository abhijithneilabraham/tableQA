
import pandas as pd
from numpy import asarray
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import tensorflow as tf

def get_keras_model():
    """Define the model."""
    model = Sequential()
    model.add(Dense(128, input_shape=[512 ,], activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(64 ,activation='relu' ,kernel_regularizer=tf.keras.regularizers.L1(0.01),
                    activity_regularizer=tf.keras.regularizers.L2(0.01)))
    model.add(Dense(6, activation='softmax'))

    model.compile(loss = 'sparse_categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
    model.summary()
    return model

data =pd.read_csv("wikidata.csv" ,usecols=["questions" ,"types"])
categories =data["types"]

x_train, x_test, y_train ,y_test =train_test_split(data["questions"], categories, shuffle=True)

import tensorflow_hub as hub

embed = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')


def get_universal_sentence_encoder(x):
    embeddings = embed(x)
    return asarray(embeddings)


train_encodings = get_universal_sentence_encoder(x_train.to_list())
test_encodings = get_universal_sentence_encoder(x_test.tolist())

y_train = asarray(y_train, dtype="float32")
y_test = asarray(y_test, dtype="float32")

model = get_keras_model()
print(train_encodings.shape)
model.fit(train_encodings, y_train, epochs=50, validation_split=0.2)

model.save("Question_Classifier.h5")

score, acc = model.evaluate(test_encodings, y_test)











