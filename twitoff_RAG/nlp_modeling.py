import spacy
from .models import Data_Hold, User
import numpy as np
from sklearn.linear_model import LogisticRegression

def convert_word2vec(text):
    
    '''
    Utilize model_w2v saved to disk to convert string to vector
    for analysis. Model is loaded from disk.
    '''

    model_w2v = spacy.load("model_word2vec")
    text_vector = model_w2v(text).vector
    return text_vector

def make_prediction(id_1, id_2, X_predict):

    '''
    Taking in two user ids, use logistic regression alongside
    spacy nlp vectorization to predict which user a hypothetical tweet
    originated from.
    '''

    # Retrieve vectors from User models
    user1 = User.query.get(id_1)
    user2 = User.query.get(id_2)
    id_1_vectors = user1.tweet_vectors
    id_2_vectors = user2.tweet_vectors
    # Combine vectors to create X
    X = np.vstack([id_1_vectors, id_2_vectors])
    # Encode labels into y
    y = np.concatenate([np.zeros(len(id_1_vectors)), np.ones(len(id_2_vectors))])
    '''Note: 0 refers to first user, 1 refers to second user'''

    model_lr = LogisticRegression().fit(X,y)
    prediction = model_lr.predict(X_predict)
    return prediction[0]
