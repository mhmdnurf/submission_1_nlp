# -*- coding: utf-8 -*-
"""fake_news.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Fo7Z7DIrtPWeNRuX19fCR7RGA4tIpZOe
"""

import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
import re

fake_news_df = pd.read_csv('fake.csv', nrows=750)
fake_news_df['status'] = 'palsu'

real_news_df = pd.read_csv('true.csv', nrows=650)
real_news_df['status'] = 'asli'

df = pd.concat([fake_news_df, real_news_df], ignore_index=True)
df = shuffle(df, random_state=22).reset_index(drop=True)

df.tail()

df = df.drop(columns=['title', 'subject', 'date'])
df.dropna(inplace=True)

def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)
df['text'] = df['text'].apply(lambda x: remove_punctuation(x.lower()))
df.head()

status = pd.get_dummies(df['status']).astype('int64')
new_df = pd.concat([df, status], axis=1)
new_df = new_df.drop(columns='status')
new_df

text_news = new_df['text'].astype('str')
status_news = new_df[['asli', 'palsu']].values

text_train, text_test, status_train, status_test = train_test_split(text_news, status_news, test_size=0.2)

tokenizer = Tokenizer(num_words=5000, oov_token='<oov>')
tokenizer.fit_on_texts(text_train)
tokenizer.fit_on_texts(text_test)

sekuens_train = tokenizer.texts_to_sequences(text_train)
sekuens_test = tokenizer.texts_to_sequences(text_test)

padded_train = pad_sequences(sekuens_train)
padded_test = pad_sequences(sekuens_test)

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=16),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(2, activation='softmax')
])
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()

class modelCallbacks(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_accuracy') > 0.98):
      print("Expected accuracy have been achieved")
      self.model.stop_training = True
cb = modelCallbacks()

model_history = model.fit(
    padded_train,
    status_train,
    epochs=100,
    validation_data=(padded_test, status_test),
    verbose=2,
    batch_size=128,
    callbacks=[cb]
  )

plt.plot(model_history.history['loss'])
plt.plot(model_history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper right')
plt.show()

plt.plot(model_history.history['accuracy'])
plt.plot(model_history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='lower right')
plt.show()

# Menguji Akurasi
sekuens_test = tokenizer.texts_to_sequences(text_test)
padded_test = pad_sequences(sekuens_test)
predictions = model.predict(padded_test)

predicted_labels = [1 if pred[1] > pred[0] else 0 for pred in predictions]
evaluation = model.evaluate(padded_test, status_test, verbose=0)
print(f"\nTest Accuracy: {evaluation[1]*100:.2f}%")

from sklearn.metrics import classification_report, confusion_matrix

print("\nClassification Report:")
print(classification_report(status_test.argmax(axis=1), predicted_labels))
print("\nConfusion Matrix:")
print(confusion_matrix(status_test.argmax(axis=1), predicted_labels))

# UJI DATA PALSU
kalimat_uji = ["House Intelligence Committee Chairman Devin Nunes is going to have a bad day. He s been under the assumption, like many of us, that the Christopher Steele-dossier was what prompted the Russia investigation so he s been lashing out at the Department of Justice and the FBI in order to protect Trump. As it happens, the dossier is not what started the investigation, according to documents obtained by the New York Times.Former Trump campaign adviser George Papadopoulos was drunk in a wine bar when he revealed knowledge of Russian opposition research on Hillary Clinton.On top of that, Papadopoulos wasn t just a covfefe boy for Trump, as his administration has alleged. He had a much larger role, but none so damning as being a drunken fool in a wine bar. Coffee boys  don t help to arrange a New York meeting between Trump and President Abdel Fattah el-Sisi of Egypt two months before the election. It was known before that the former aide set up meetings with world leaders for Trump, but team Trump ran with him being merely a coffee boy.In May 2016, Papadopoulos revealed to Australian diplomat Alexander Downer that Russian officials were shopping around possible dirt on then-Democratic presidential nominee Hillary Clinton. Exactly how much Mr. Papadopoulos said that night at the Kensington Wine Rooms with the Australian, Alexander Downer, is unclear,  the report states.  But two months later, when leaked Democratic emails began appearing online, Australian officials passed the information about Mr. Papadopoulos to their American counterparts, according to four current and former American and foreign officials with direct knowledge of the Australians  role. Papadopoulos pleaded guilty to lying to the F.B.I. and is now a cooperating witness with Special Counsel Robert Mueller s team.This isn t a presidency. It s a badly scripted reality TV show.Photo by Win McNamee/Getty Images."]

sekuens_uji = tokenizer.texts_to_sequences(kalimat_uji)
padded_uji = pad_sequences(sekuens_uji)

prediksi_uji = model.predict(padded_uji)

label_uji = 1 if prediksi_uji[0, 1] > prediksi_uji[0, 0] else 0

# Menampilkan hasil prediksi
if label_uji == 1:
    print("Kalimat tersebut diprediksi sebagai PALSU.")
else:
    print("Kalimat tersebut diprediksi sebagai ASLI.")

# UJI DATA ASLI
kalimat_uji = ["White House, Congress prepare for talks on spending, immigration."]

sekuens_uji = tokenizer.texts_to_sequences(kalimat_uji)
padded_uji = pad_sequences(sekuens_uji)
prediksi_uji = model.predict(padded_uji)
label_uji = 1 if prediksi_uji[0, 1] > prediksi_uji[0, 0] else 0

# Menampilkan hasil prediksi
if label_uji == 1:
    print("Kalimat tersebut diprediksi sebagai PALSU.")
else:
    print("Kalimat tersebut diprediksi sebagai ASLI.")

