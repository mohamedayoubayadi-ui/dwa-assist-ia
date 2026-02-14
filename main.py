import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de la page
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# Masquer le menu pour un look plus "App"
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- RÉCUPÉRATION DE LA CLÉ API ---
try:
    # Utilisation des secrets Streamlit pour la version en ligne
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("❌ Erreur : Clé 'GOOGLE_API_KEY' introuvable dans les Secrets Streamlit.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.success("✅ Bakhana est actif")
    system_instruction = "Tu es Bakhana, un assistant pharmacien virtuel bienveillant qui aide les personnes âgées."
    uploaded_file = st.file_uploader("Prendre une photo du médicament", type=["jpg", "png", "jpeg"])

# --- TITRE ---
st.title("💊 Bakhana : Dwa-Assist")
st.markdown("### Votre Pharmacien IA Intelligent (Vision & Voix 🗣️)")
st.markdown("---")

col1, col2 = st.columns([1, 1]) 

# --- COLONNE GAUCHE (Image) ---
with col1:
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, use_column_width=True)
    else:
        st.info("👈 Chargez une photo pour commencer l'analyse.")

# --- COLONNE DROITE (Analyse) ---
with col2:
    st.subheader("Analyse de Bakhana")
    user_prompt = st.text_area("Avez-vous une question spécifique ?", placeholder="Ex: Est-ce pour la fièvre ?")
    
    if st.button("Lancer l'analyse 🚀", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Merci d'ajouter une photo d'abord.")
        else:
            try:
                genai.configure(api_key=api_key)
                # MODIFICATION ICI : Utilisation du nom de modèle universel pour éviter l'erreur 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner('🧠 Bakhana examine le médicament...'):
                    # SYNTAXE CORRIGÉE : Les guillemets sont bien refermés
                    prompt_final = f"""
                    Analyse cette image de médicament.
                    Donne-moi UNIQUEMENT ces 3 points de manière très claire :
                    1. NOM et USAGE (C'est quoi et pour quoi ?)
                    2. DOSAGE (Comment le prendre ?)
                    3. PRÉCAUTION (Y a-t-il un danger ?)
                    
                    Note du patient : {user_prompt if user_prompt else "Analyse générale."}
                    Réponds comme un pharmacien très doux.
                    """ 
                    
                    # On repasse l'image pour l'analyse
                    img = Image.open(uploaded_file)
                    response = model.generate_content([system_instruction, prompt_final, img])
                
                # SÉCURITÉ : On vérifie que response existe avant de l'afficher (Évite le NameError)
                if response and response.text:
                    st.markdown("### 📋 Résultat :")
                    st.write(response.text)
                    
                    # GÉNÉRATION AUDIO
                    try:
                        # On retire les étoiles pour un son propre (pas d'"astérisque astérisque")
                        clean_text = response.text.replace("*", "")
                        tts = gTTS(text=clean_text, lang='fr')
                        tts.save("audio_bakhana.mp3")
                        st.audio("audio_bakhana.mp3")
                    except Exception as e_audio:
                        st.warning("Lecture vocale momentanément indisponible.")
                else:
                    st.error("L'IA n'a pas pu lire l'image. Essayez une photo plus nette.")

            except Exception as e:
                # Gestion générique de l'erreur 404 ou autre
                st.error(f"Désolé, une erreur technique est survenue : {e}")