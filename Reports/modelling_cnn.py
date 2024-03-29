from functools import reduce
from keras.layers import GlobalMaxPool1D, Conv1D
from keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint
from keras_preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from itertools import chain
import warnings
import operator
from collections import Counter
import pandas as pd
from keras.layers import Embedding
from Reports.helper_functions import accuracy
from keras.callbacks import ReduceLROnPlateau
from keras.layers.core import Activation, Dropout, Dense
from keras.models import Sequential
from keras.utils import np_utils

warnings.filterwarnings("ignore")
import numpy as np
import el_core_news_sm

nlp = el_core_news_sm.load()

dataframe=pd.read_csv("data/preprocessed/decisions_lemmas.csv")

def tokenizeSentences(sent):
    doc = nlp(sent)
    sentences = [sent.string.strip() for sent in doc]
    return sentences

def word_freq(Xs, num):
    all_words = [words.lower() for sentences in Xs for words in sentences]
    sorted_vocab = sorted(dict(Counter(all_words)).items(), key=operator.itemgetter(1))
    final_vocab = [k for k,v in sorted_vocab if v > num]
    word_idx = dict((c, i + 1) for i, c in enumerate(final_vocab))
    return final_vocab, word_idx

'''
H παρακάτω συνάρτηση θα μοιράσει τις λέξεις που έχουμε 
'''
def vectorize_sentences(data, word_idx, final_vocab, maxlen=128):
    X = []
    paddingIdx = len(final_vocab)+2
    for sentences in data:
        x=[]
        for word in sentences:
            if word in final_vocab:
                x.append(word_idx[word])
            elif word.lower() in final_vocab:
                x.append(word_idx[word.lower()])
            else:
                x.append(paddingIdx)
        X.append(x)
    return (pad_sequences(X, maxlen=maxlen))


###################################################
nsk_list = dataframe['Category'].tolist()
nsk_list = [(str(x)).split(',') for x in nsk_list]

for idx, lst in enumerate(nsk_list):
    cats = [x.strip() for x in lst]
    dataframe.at[idx, 'Category'] = cats
nsk_list = list(chain.from_iterable(nsk_list))
nsk_list = [x.strip() for x in nsk_list]
nsk_set = set(nsk_list)

categories = (list(nsk_set))

categories.sort()
categories_accumulator = [0]*len(categories)

for index, row in dataframe.iterrows():
    cats = row['Category']
    for cat in cats:
        accumulator_idx = categories.index(cat)
        categories_accumulator[accumulator_idx] +=1

sorted_indexes = sorted(range(len(categories_accumulator)), key=lambda k: categories_accumulator[k], reverse=True)
categories_accumulator.sort(reverse=True)
categories.sort()


lemmata = []
lemmata.extend(dataframe['Category'].tolist())
lemmata = [list(filter(None, empty)) for empty in lemmata]

dataframe['New_Category'] = lemmata
decisions_new = dataframe[~(dataframe['New_Category'].str.len() == 0)]

all_categories =  sum(lemmata,[])
len(all_categories)
len(set(all_categories))
import nltk
decisions_new['Lemmata'] = decisions_new['New_Category'].apply(lambda text : len(str(text).split(',')))

decisions_new.Lemmata.value_counts()
all_categories_new =  nltk.FreqDist(all_categories)

count_lemmas = pd.DataFrame({'Lemma': list(all_categories_new.keys()),
                                 'Count': list(all_categories_new.values())})
count_lemmas_sorted = count_lemmas.sort_values(['Count'],ascending=False)
lemma_counts = count_lemmas_sorted['Count'].values

sorted_idx = count_lemmas_sorted.index
sorted_idx = list(sorted_idx)

lemmata_new = list(count_lemmas['Lemma'])
new_lemmata = [lemmata_new[word] for word in sorted_idx[25:65]]
new_categories = decisions_new['New_Category']

for idx, row in decisions_new.iterrows():
    cats = row['New_Category']
    new_cats = []
    for cat in cats:
        if cat in new_lemmata:
            new_cats.append(cat)
    decisions_new.at[idx, 'New_Category'] = new_cats

columns = ['index', 'Category', 'Lemmata']
decisions_new.drop(columns, axis=1, inplace=True)

decisions_new = decisions_new[decisions_new['New_Category'].map(lambda d: len(d))> 0]
decisions_new = decisions_new.reset_index(drop=True)

y = np.array([np.array(x) for x in decisions_new.New_Category.values.tolist()])
mlb = MultiLabelBinarizer()
y_1= mlb.fit_transform(y)
lemma_columns = mlb.classes_

decisions_new = decisions_new.join(pd.DataFrame(mlb.fit_transform(decisions_new.pop('New_Category')),
                                                columns=mlb.classes_,
                                                index=decisions_new.index))
Xs = []
for texts in decisions_new.Concultatory:
    Xs.append(tokenizeSentences(texts))
vocab = sorted(reduce(lambda x, y: x | y, (set(words) for words in Xs)))
len(vocab)

final_vocab, word_idx = word_freq(Xs,2)
vocab_len = len(final_vocab)

# new_y = pd.DataFrame(decisions_new.drop(['Title', 'Concultatory'], axis=1, inplace=True))
train_data = vectorize_sentences(Xs, word_idx, final_vocab)


x_train, x_test, y_train, y_test = train_test_split(train_data, y_1, test_size=0.2, random_state=42)

y_train_df = pd.DataFrame(y_train)

y_train_df.columns = ['ΑΔΕΙΑ ΙΔΡΥΣΕΩΣ ΛΕΙΤΟΥΡΓΙΑΣ', 'ΑΔΕΙΕΣ ΔΙΑΦΟΡΕΣ ΕΙΔΙΚΕΣ', 'ΑΕΙ ΔΕΠ',
       'ΑΛΛΟΔΑΠΗ', 'ΑΜΟΙΒΕΣ', 'ΑΝΩΤΑΤΑ ΕΚΠΑΙΔΕΥΤΙΚΑ ΙΔΡΥΜΑΤΑ',
       'ΑΝΩΤΕΡΑ ΒΙΑ', 'ΑΞΙΩΜΑΤΙΚΟΙ', 'ΑΠΟΣΠΑΣΗ',
       'ΑΡΜΟΔΙΟΤΗΤΕΣ ΟΡΓΑΝΩΝ ΔΙΟΙΚΗΣΕΩΣ', 'ΔΑΠΑΝΕΣ',
       'ΔΙΕΥΘΥΝΤΗΣ ΠΡΟΙΣΤΑΜΕΝΟΣ', 'ΕΚΠΑΙΔΕΥΣΗ', 'ΕΚΠΑΙΔΕΥΤΙΚΟΙ ΥΠΑΛΛΗΛΟΙ',
       'ΕΛΕΓΧΟΣ ΝΟΜΙΜΟΤΗΤΑΣ', 'ΕΝΙΣΧΥΣΕΙΣ ΕΠΙΔΟΤΗΣΕΙΣ', 'ΕΠΙΣΤΡΟΦΗ',
       'ΕΤΑΙΡΕΙΕΣ', 'ΙΔΙΩΤΙΚΟ ΠΡΟΣΩΠΙΚΟ ΔΗΜΟΣΙΟΥ',
       'ΙΔΡΥΜΑ ΚΟΙΝΩΝΙΚΩΝ ΑΣΦΑΛΙΣΕΩΝ', 'ΙΚΑ-ΕΤΑΜ',
       'ΚΟΙΝΟΤΙΚΕΣ ΟΔΗΓΙΕΣ ΚΑΝΟΝΙΣΜΟΙ', 'ΚΟΙΝΟΤΙΚΟ ΔΙΚΑΙΟ', 'ΜΕΛΕΤΕΣ',
       'ΜΕΛΗ', 'ΜΙΣΘΩΣΗ ΕΡΓΟΥ', 'ΝΠΔΔ', 'ΝΠΙΔ', 'ΠΑΡΑΓΡΑΦΗ',
       'ΠΙΣΤΟΠΟΙΗΤΙΚΑ ΒΕΒΑΙΩΣΕΙΣ', 'ΠΟΛΕΟΔΟΜΙΑ ΡΥΜΟΤΟΜΙΑ',
       'ΠΤΥΧΙΑ ΤΙΤΛΟΙ ΣΠΟΥΔΩΝ', 'ΣΥΓΚΡΟΤΗΣΗ ΣΥΝΘΕΣΗ', 'ΣΥΛΛΟΓΙΚΑ ΟΡΓΑΝΑ',
       'ΣΥΜΒΑΣΗ ΠΡΟΜΗΘΕΙΑΣ', 'ΣΥΜΜΕΤΟΧΗ', 'ΣΥΝΤΑΞΕΙΣ',
       'ΤΑΜΕΙΑ ΑΣΦΑΛΙΣΤΙΚΑ', 'ΦΟΡΟΛΟΓΙΑ ΕΙΣΟΔΗΜΑΤΟΣ',
       'ΧΟΡΗΓΗΣΗ ΑΝΤΙΓΡΑΦΩΝ ΕΓΓΡΑΦΩΝ']
y_test_df = pd.DataFrame(y_test)
y_test_df.columns = ['ΑΔΕΙΑ ΙΔΡΥΣΕΩΣ ΛΕΙΤΟΥΡΓΙΑΣ', 'ΑΔΕΙΕΣ ΔΙΑΦΟΡΕΣ ΕΙΔΙΚΕΣ', 'ΑΕΙ ΔΕΠ',
       'ΑΛΛΟΔΑΠΗ', 'ΑΜΟΙΒΕΣ', 'ΑΝΩΤΑΤΑ ΕΚΠΑΙΔΕΥΤΙΚΑ ΙΔΡΥΜΑΤΑ',
       'ΑΝΩΤΕΡΑ ΒΙΑ', 'ΑΞΙΩΜΑΤΙΚΟΙ', 'ΑΠΟΣΠΑΣΗ',
       'ΑΡΜΟΔΙΟΤΗΤΕΣ ΟΡΓΑΝΩΝ ΔΙΟΙΚΗΣΕΩΣ', 'ΔΑΠΑΝΕΣ',
       'ΔΙΕΥΘΥΝΤΗΣ ΠΡΟΙΣΤΑΜΕΝΟΣ', 'ΕΚΠΑΙΔΕΥΣΗ', 'ΕΚΠΑΙΔΕΥΤΙΚΟΙ ΥΠΑΛΛΗΛΟΙ',
       'ΕΛΕΓΧΟΣ ΝΟΜΙΜΟΤΗΤΑΣ', 'ΕΝΙΣΧΥΣΕΙΣ ΕΠΙΔΟΤΗΣΕΙΣ', 'ΕΠΙΣΤΡΟΦΗ',
       'ΕΤΑΙΡΕΙΕΣ', 'ΙΔΙΩΤΙΚΟ ΠΡΟΣΩΠΙΚΟ ΔΗΜΟΣΙΟΥ',
       'ΙΔΡΥΜΑ ΚΟΙΝΩΝΙΚΩΝ ΑΣΦΑΛΙΣΕΩΝ', 'ΙΚΑ-ΕΤΑΜ',
       'ΚΟΙΝΟΤΙΚΕΣ ΟΔΗΓΙΕΣ ΚΑΝΟΝΙΣΜΟΙ', 'ΚΟΙΝΟΤΙΚΟ ΔΙΚΑΙΟ', 'ΜΕΛΕΤΕΣ',
       'ΜΕΛΗ', 'ΜΙΣΘΩΣΗ ΕΡΓΟΥ', 'ΝΠΔΔ', 'ΝΠΙΔ', 'ΠΑΡΑΓΡΑΦΗ',
       'ΠΙΣΤΟΠΟΙΗΤΙΚΑ ΒΕΒΑΙΩΣΕΙΣ', 'ΠΟΛΕΟΔΟΜΙΑ ΡΥΜΟΤΟΜΙΑ',
       'ΠΤΥΧΙΑ ΤΙΤΛΟΙ ΣΠΟΥΔΩΝ', 'ΣΥΓΚΡΟΤΗΣΗ ΣΥΝΘΕΣΗ', 'ΣΥΛΛΟΓΙΚΑ ΟΡΓΑΝΑ',
       'ΣΥΜΒΑΣΗ ΠΡΟΜΗΘΕΙΑΣ', 'ΣΥΜΜΕΤΟΧΗ', 'ΣΥΝΤΑΞΕΙΣ',
       'ΤΑΜΕΙΑ ΑΣΦΑΛΙΣΤΙΚΑ', 'ΦΟΡΟΛΟΓΙΑ ΕΙΣΟΔΗΜΑΤΟΣ',
       'ΧΟΡΗΓΗΣΗ ΑΝΤΙΓΡΑΦΩΝ ΕΓΓΡΑΦΩΝ']

category_columns = y_train_df.columns

#LABEL POWERSET METHOD
train_y_labels= y_train_df.groupby(list(lemma_columns)).ngroup()
#look up table y_labels
y_labels_lut = y_train_df.copy(deep=True)
y_labels_lut['Labels'] = train_y_labels
y_labels_lut = y_labels_lut.drop_duplicates()
y_labels_lut = y_labels_lut.reset_index(drop=True).set_index('Labels').sort_index()

# One-hot encoding the output labels
num_classes = y_labels_lut.shape[0]
train_y_onehot = np_utils.to_categorical(train_y_labels, num_classes = num_classes)

###################################
from keras.regularizers import l2
####################################################################
filter_length = 256
cnn_model= Sequential()
cnn_model.add(Embedding(vocab_len+3, 100, input_length=x_train.shape[1]))
cnn_model.add(Dropout(0.2))
cnn_model.add(Conv1D(filter_length, 8))
cnn_model.add(GlobalMaxPool1D())
cnn_model.add(Dense(814))
cnn_model.add(Activation('softmax'))

cnn_model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
cnn_model.summary()

callbacks = [
    ReduceLROnPlateau(),
    EarlyStopping(patience=4),
    ModelCheckpoint(filepath='data/models/modelcnn.h5', save_best_only=True)
]
cnn_history = cnn_model.fit(x_train, train_y_onehot,
                    class_weight='auto',
                    epochs=20,
                    batch_size=32,
                    # validation_split=0.1,
                    callbacks=callbacks)


y_pred = cnn_model.predict(x_test)
y_pred_label = pd.DataFrame(np.argmax(y_pred, axis=1))
predictions = pd.merge(y_pred_label, y_labels_lut, how='left', left_on=0, right_on='Labels')[category_columns]
print(accuracy(y_test_df, predictions))

lp_cnn = accuracy(y_test_df, predictions)
lp_cnn.to_excel('data/Results/lp_cnn.xlsx')

###########################
# Binary Relevance Method
prob_thresh = (y_train_df.sum()/y_train_df.shape[0]).clip(upper=0.5)
prob_thresh
from keras.regularizers import l2
####################################################################
filter_length = 256
cnn_model= Sequential()
cnn_model.add(Embedding(vocab_len+3, 300, input_length=x_train.shape[1]))
cnn_model.add(Dropout(0.2))
cnn_model.add(Conv1D(filter_length, 5, padding='valid', activation='relu', strides=1))
cnn_model.add(GlobalMaxPool1D())
cnn_model.add(Dense(y_train_df.shape[1]))
cnn_model.add(Activation('sigmoid'))

cnn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
cnn_model.summary()

callbacks = [
    ReduceLROnPlateau(),
    EarlyStopping(patience=5),
    ModelCheckpoint(filepath='data/models/modelcnn.h5', save_best_only=True)
]
history = cnn_model.fit(x_train, y_train_df,
                    class_weight='auto',
                    epochs=50,
                    batch_size=32,
                    # validation_split=0.1,
                    callbacks=callbacks)
###################################
print ("\nΑναφορά Κατηγοριοποίησης")
y_pred = cnn_model.predict(x_test)
predictions = pd.DataFrame(index=y_test_df.index, columns=y_test_df.columns)

for i in range(y_pred.shape[0]):
  predictions.iloc[i,:] = (y_pred[i,:] > prob_thresh).map({True:1, False:0})
print(accuracy(y_test_df, predictions))

BR_cnn = accuracy(y_test_df, predictions)
BR_cnn.to_excel('data/Results/br_cnn_titles.xlsx')



###########
# word2vec#
###########
import os
embeddings_index = {}
f = open(os.path.join('', 'data/embeddings/embeddings_word2vec.txt'), encoding= "utf-8")
for line in f :
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:])
    embeddings_index[word] = coefs
f.close()

#Λεξικό
num_words = len(word_idx) + 1
embeddings_matrix = np.zeros((num_words, 100))

for w, i in word_idx.items():
    if i > num_words:
        continue
    embeddings_vector = embeddings_index.get(w)
    if embeddings_vector is not None:
        embeddings_matrix[i] = embeddings_vector

prob_thresh = (y_train_df.sum()/y_train_df.shape[0]).clip(upper=0.5)
prob_thresh
from keras.initializers import Constant
####################################################################
filter_length = 256
cnn_model= Sequential()
cnn_model.add(Embedding(vocab_len+3, 300, embeddings_initializer=Constant(embeddings_matrix),
                        input_length=x_train.shape[1]))
cnn_model.add(Dropout(0.2))
cnn_model.add(Conv1D(filter_length, 4, padding='same'))
cnn_model.add(GlobalMaxPool1D())
cnn_model.add(Dense(y_train_df.shape[1]))
cnn_model.add(Activation('sigmoid'))

cnn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
cnn_model.summary()

callbacks = [
    ReduceLROnPlateau(),
    EarlyStopping(patience=4),
    ModelCheckpoint(filepath='data/models/modelcnn.h5', save_best_only=True)
]
cnn_history = cnn_model.fit(x_train, y_train_df,
                    class_weight='auto',
                    epochs=20,
                    batch_size=32,
                    # validation_split=0.1,
                    callbacks=callbacks)
###################################
print ("\nΑναφορά Κατηγοριοποίησης")
y_pred = cnn_model.predict(x_test)
predictions = pd.DataFrame(index=y_test_df.index, columns=y_test_df.columns)

for i in range(y_pred.shape[0]):
  predictions.iloc[i,:] = (y_pred[i,:] > prob_thresh).map({True:1, False:0})
print(accuracy(y_test_df, predictions))
w2vec = accuracy(y_test_df, predictions)
w2vec.to_excel('data/Results/w2vec_titles.xlsx')

