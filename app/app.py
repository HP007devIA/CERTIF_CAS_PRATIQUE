import streamlit as st
import cv2
import numpy as np
import json
import joblib
import tensorflow as tf
from PIL import Image
from routes import *
from functions import preprocess_img, detect_GOD, recherche_ID

# Chargement des modèles et encodeurs
encodeur_OD = joblib.load(OD_ENCODER_PATH)
encodeur_OG = joblib.load(OG_ENCODER_PATH)
encodeur_GOD = joblib.load(GOD_ENCODER_PATH)

model_OG = tf.keras.models.load_model(OG_CLASSIFIER_PATH)
model_OG.trainable = False
model_OD = tf.keras.models.load_model(OD_CLASSIFIER_PATH)
model_OD.trainable = False
model_GOD = tf.keras.models.load_model(GOD_CLASSIFIER_PATH)
model_GOD.trainable = False

# Fonction pour afficher l'interface utilisateur
def main():
    # Lire le contenu du fichier CSS depuis le dossier "static"
    with open('static/style.css', 'r') as file:
        css = file.read()
    
    # Configurer la page Streamlit
    st.set_page_config(
        page_title="Reconnaissance d'employés par iris",
        page_icon="static/eye.png",
        layout="wide"
    )

    # Ajouter le contenu du fichier CSS à l'application Streamlit
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    st.title("Application d'Authentification")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Sélection d'image")
        image = st.file_uploader("Sélectionnez une image", type=['jpg', 'png', 'jpeg', 'bmp'])

    with col2:
        # st.write("Image sélectionnée")
        if image is not None:
            process_image(image)

# Fonction pour traiter l'image téléchargée
def process_image(image):
    image = Image.open(image)
    image = np.array(image)

    # Prétraiter l'image
    image_prep = preprocess_img(image)

    # Prédiction et affichage des résultats
    detect_and_display(image, image_prep)

# Fonction pour détecter et afficher les résultats
def detect_and_display(image, image_prep):
    col1, col2, col3 = st.columns(3)

    # Afficher l'image
    with col1:
        st.image(image, use_column_width=True)
        
        detect_eye, reliability = detect_GOD(image_prep)

        if detect_eye == 0:
            eye = "DROIT"
            probs = model_OD.predict(np.array([image_prep]))
            prediction_user = np.argmax(probs)
            decoded_prediction_user = encodeur_OD.inverse_transform([prediction_user])
        else:
            eye = "GAUCHE"
            probs = model_OG.predict(np.array([image_prep]))
            prediction_user = np.argmax(probs)
            decoded_prediction_user = encodeur_OG.inverse_transform([prediction_user])
        
        st.markdown(f"<p class='eyeDetection'>Oeil {eye}", unsafe_allow_html=True)

    # Prédire les caractéristiques
    with col2:

        nom, annee_embauche, genre, poste = recherche_ID(decoded_prediction_user[0])
        
        table_data = [
            ("ID", decoded_prediction_user[0]),
            ("Nom", nom),
            ("Année d'embauche", annee_embauche),
            ("Genre", genre),
            ("Poste", poste)
        ]

        left_column_style = "leftColumn"
        right_column_style = "rightColumn"
        table_html = "<table class='tableStyle'>"

        for label, value in table_data:
            table_html += f"<tr><td class='{left_column_style}'>{label}</td><td class='{right_column_style}'>{value}</td></tr>"
        
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    
    with col3:
        st.write(f"Précision : {reliability}%")
        if reliability < 33:
            st.markdown('<div class="redJauge"></div>', unsafe_allow_html=True)
        elif reliability < 66:
            st.markdown('<div class="orangeJauge"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="greenJauge"></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()