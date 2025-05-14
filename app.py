import streamlit as st
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import pandas as pd
import plotly.express as px

# --------------------- Configuration de la page ---------------------
st.set_page_config(page_title="🩺 Détection de maladies via images", layout="centered")

# --------------------- Style personnalisé ---------------------
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f5;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #5cb85c;
        color: white;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------- Classes du modèle ---------------------
classes = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Background_without_leaves', 'Blueberry___healthy', 'Cherry___Powdery_mildew', 'Cherry___healthy',
    'Corn___Cercospora_leaf_spot Gray_leaf_spot', 'Corn___Common_rust', 'Corn___Northern_Leaf_Blight', 'Corn___healthy',
    'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

# --------------------- Descriptions des maladies ---------------------
descriptions = {
    "Apple___Black_rot": "🍎 Maladie fongique des pommes causée par *Botryosphaeria obtusa*.",
    "Tomato___Early_blight": "🍅 Maladie causée par *Alternaria solani*, affecte les feuilles, tiges et fruits.",
    "Corn___Common_rust": "🌽 Taches brun rougeâtre causées par *Puccinia sorghi*.",
    "Potato___Late_blight": "🥔 Infection grave causée par *Phytophthora infestans*.",
    "Grape___Black_rot": "🍇 Champignon *Guignardia bidwellii* provoquant des lésions noires.",
    "Peach___Bacterial_spot": "🍑 Bactéries causant des taches foncées sur les feuilles et fruits.",
    "Tomato___Leaf_Mold": "🍅 Moisissure foliaire due à *Passalora fulva*.",
}

# --------------------- Chargement du modèle ---------------------
model = load_model("deseas_Predction_Images_Classification_CNN.keras")

# --------------------- Fonctions ---------------------
def preprocess_image(image):
    image = image.resize((164, 164))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict(image):
    processed = preprocess_image(image)
    prediction = model.predict(processed)[0]
    return prediction

# --------------------- Interface utilisateur ---------------------
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🩺 Détection de maladies végétales")
    st.markdown("Téléversez une **image de feuille ou de fruit**, et le modèle prédit s’il y a une **maladie** 🧠")
with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/2909/2909764.png", width=110)

uploaded_file = st.file_uploader("📤 Téléversez une image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Image téléversée", use_column_width=True)

    if st.button("🔍 Prédire"):
        with st.spinner("🧪 Analyse en cours..."):
            predictions = predict(image)
            predicted_class = classes[np.argmax(predictions)]
            confidence = np.max(predictions)

        st.success(f"✅ **Classe prédite :** `{predicted_class}`")
        st.markdown(f"🧾 **Confiance :** `{confidence:.2%}`")

        # Description si disponible
        if predicted_class in descriptions:
            st.info(f"ℹ️ {descriptions[predicted_class]}")

        # Affichage top 5
        df = pd.DataFrame({
            'Classe': classes,
            'Probabilité': predictions
        }).sort_values(by="Probabilité", ascending=False)

        top_df = df.head(5)

        st.markdown("### 📊 Top 5 des prédictions")
        st.dataframe(top_df.reset_index(drop=True))

        # Graphique interactif
        fig = px.bar(top_df, x="Probabilité", y="Classe", orientation="h", color="Probabilité",
                     color_continuous_scale="Agsunset", text_auto='.2%')
        st.plotly_chart(fig, use_container_width=True)

        # Barre de confiance
        st.markdown("### 🔎 Niveau de confiance global")
        st.progress(float(confidence))

        # Bouton de téléchargement
        report = f"Classe prédite : {predicted_class}\nConfiance : {confidence:.2%}"
        st.download_button("📥 Télécharger le rapport", data=report, file_name="rapport_prediction.txt")
