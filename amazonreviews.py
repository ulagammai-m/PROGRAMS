# -*- coding: utf-8 -*-
"""amazonreviews.ipynb
Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aXTxlbF121HJm3SxZSi3aaNsBx-QensN
"""

import tensorflow as tf
num_gpus_available = len(tf.config.experimental.list_physical_devices('GPU'))
print("Num GPUs Available: ", num_gpus_available)
#assert num_gpus_available > 0
!pip install transformers
!pip install transformers
from transformers import DistilBertTokenizerFast
from transformers import TFDistilBertForSequenceClassification
import pandas as pd
import numpy as np

import nltk
import re
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

!pip install tensorflow_datasets

import tensorflow_datasets as tfds
ds = tfds.load('amazon_us_reviews/Mobile_Electronics_v1_00', split='train', shuffle_files=True)
assert isinstance(ds, tf.data.Dataset)
print(ds)

df = tfds.as_dataframe(ds)

df["Sentiment"] = df["data/star_rating"].apply(lambda score: "positive" if score >= 3 else "negative")
df['Sentiment'] = df['Sentiment'].map({'positive':1, 'negative':0})

df['short_review'] =df['data/review_body'].str.decode("utf-8")

df = df[["short_review", "Sentiment"]]

# Dropping last n rows using drop
n = 54975
df.drop(df.tail(n).index,
        inplace = True)

index = df.index
number_of_rows = len(index)
print(number_of_rows)

df.tail()

df.head()

reviews = df['short_review'].values.tolist()
labels = df['Sentiment'].tolist()

print(reviews[:2])
print(labels[:2])

from sklearn.model_selection import train_test_split
training_sentences, validation_sentences, training_labels, validation_labels = train_test_split(reviews, labels, test_size=.2)

tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

tokenizer([training_sentences[0]], truncation=True,
                            padding=True, max_length=128)

train_encodings = tokenizer(training_sentences,
                            truncation=True,
                            padding=True)
val_encodings = tokenizer(validation_sentences,
                            truncation=True,
                            padding=True)

train_dataset = tf.data.Dataset.from_tensor_slices((
    dict(train_encodings),
    training_labels
))

val_dataset = tf.data.Dataset.from_tensor_slices((
    dict(val_encodings),
    validation_labels
))

model = TFDistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased',num_labels=2)

optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5, epsilon=1e-08)
model.compile(optimizer=optimizer, loss=model.hf_compute_loss, metrics=['accuracy'])
model.fit(train_dataset.shuffle(100).batch(16),
          epochs=2,
          batch_size=16,
          validation_data=val_dataset.shuffle(100).batch(16))

model.save_pretrained("./sentiment")

loaded_model = TFDistilBertForSequenceClassification.from_pretrained("./sentiment")

test_sentence = "This is a really good product. I love it"


predict_input = tokenizer.encode(test_sentence,
                                 truncation=True,
                                 padding=True,
                                 return_tensors="tf")

tf_output = loaded_model.predict(predict_input)[0]


tf_prediction = tf.nn.softmax(tf_output, axis=1)
labels = ['Negative','Positive']
label = tf.argmax(tf_prediction, axis=1)
label = label.numpy()
print(labels[label[0]])
