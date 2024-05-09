import cv2
import numpy as np
import json
import joblib
import tensorflow as tf
import matplotlib.pyplot as plt
from routes import *

encodeur_OD = joblib.load(OD_ENCODER_PATH)
encodeur_OG = joblib.load(OG_ENCODER_PATH)
encodeur_ODG = joblib.load(GOD_ENCODER_PATH)

model_OG = tf.keras.models.load_model(OG_CLASSIFIER_PATH)
model_OG.trainable = False
model_OD = tf.keras.models.load_model(OD_CLASSIFIER_PATH)
model_OD.trainable = False
model_ODG = tf.keras.models.load_model(GOD_CLASSIFIER_PATH)
model_ODG.trainable = False

# Fonction de prétraitement de l'image
def preprocess_img(img, new_dim=(240, 320)):
    new_img = cv2.resize(img, (new_dim[1], new_dim[0]), interpolation=cv2.INTER_AREA)
    new_img = new_img / 255
    return new_img

def recherche_ID(prediction_user):
    with open(EMPLOYEES_INFO_PATH, 'r') as json_file:
        data = json.load(json_file)
    info = data[str(prediction_user)]
    nom = info['nom']
    annee_embauche = info['annee_embauche']
    genre = info['genre']
    poste = info['poste']
    return nom,annee_embauche,genre,poste

def detect_GOD(image):
    probs=model_ODG.predict(np.array([image]))
    prediction = np.argmax(probs)             
    decode_prediction = encodeur_ODG.inverse_transform([prediction])
    fiabilite = round(float(probs[0][prediction]),4)
    fiabilite *=100
    return decode_prediction, fiabilite