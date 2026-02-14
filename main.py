import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de la page (Onglet du navigateur)
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# CSS pour cacher le menu Streamlit et le footer pour un look plus pro
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- RÉCUPÉRATION AUTOMATIQUE DE LA CLÉ API ---
# On récupère la clé depuis les "Advanced Settings" de Streamlit Cloud
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("❌ La clé API n'est pas configurée dans les Secrets de Streamlit.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.success("✅ Connexion à Bakhana établie")
    
    # Instruction système pour définir la personnalité de l'IA
    system_instruction = """
    Tu es Bakhana, l'assistant intelligent du projet Dwa-Assist. 
    Ton rôle est d'aider les personnes à comprendre leurs médicaments de manière simple et rassurante.
    """
    
    st.info("💡 Conseil : Prenez une photo bien nette du nom du médicament.")

# --- TITRE PRINCIPAL ---
st.title("💊 Bakhana : Dwa-Assist")
st.markdown("### Votre Pharmacien IA Intelligent (Vision & Voix 🗣️)")
st.markdown("---")

# Création de deux colonnes pour l'interface
col1, col2 = st.columns([1, 1]) 

# Upload de l'image dans la barre latérale ou la colonne 1
uploaded_file = st.sidebar.file_uploader("Prendre une photo du médicament", type=["jpg", "png", "jpeg"])
image_data = None

# --- COLONNE GAUCHE (Affichage de l'image) ---
with col1:
    if uploaded_file:
        st.success("📸 Image chargée avec succès")
        image_data = Image.open(uploaded_file)
        st.image(image_data, use_column_width=True)
    else:
        st.info("👈 Chargez une photo de la boîte ou de l'ordonnance pour commencer.")

# --- COLONNE DROITE (Analyse et Audio) ---
with col2:
    st.subheader("Analyse de Bakhana")
    user_prompt = st.text_area("Une question particulière ? (Laissez vide pour une analyse générale)", height=100)
    
    # BOUTON D'ENVOI
    if st.button("Analyser le médicament 🚀", type="primary", use_container_width=True):
        if not image_data:
            st.warning("⚠️ Veuillez d'abord charger une image.")
        else:
            try:
                # Configuration de Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner('🧠 Bakhana examine le document...'):
                    # Préparation du prompt pour forcer une réponse courte et structurée
                    prompt_final = f"""
                    Analyse cette image de