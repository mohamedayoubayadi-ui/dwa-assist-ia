import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de l'interface
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# --- RÉCUPÉRATION CLÉ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("❌ Erreur : Clé 'GOOGLE_API_KEY' introuvable dans les Secrets de Streamlit.")
    st.stop()

# --- FONCTION MAGIQUE : DÉTECTION DU MODÈLE VALIDE ---
def get_working_model_name():
    """Cherche dynamiquement un modèle qui accepte les images sur ce compte."""
    try:
        for m in genai.list_models():
            # On cherche un modèle qui supporte la génération de contenu et qui n'est pas uniquement textuel
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    return m.name
        return "gemini-1.5-flash" # Fallback par défaut
    except Exception:
        return "gemini-1.5-flash"

# --- INTERFACE UTILISATEUR ---
st.title("💊 Bakhana : Dwa-Assist")
st.markdown("### Votre Pharmacien IA Intelligent (Vision & Voix 🗣️)")
st.divider()

with st.sidebar:
    st.header("⚙️ Paramètres")
    uploaded_file = st.file_uploader("Prendre une photo du médicament", type=["jpg", "png", "jpeg"])
    st.success("Bakhana est prêt à vous aider.")

col1, col2 = st.columns(2)

# --- COLONNE GAUCHE (Image) ---
with col1:
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True, caption="Image chargée")
    else:
        st.info("👈 Veuillez charger une photo (boîte ou ordonnance).")

# --- COLONNE DROITE (Analyse) ---
with col2:
    st.subheader("Analyse de Bakhana")
    user_query = st.text_area("Question optionnelle :", placeholder="Ex: C'est pour quel symptôme ?")
    
    if st.button("Lancer l'analyse 🚀", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Merci de charger une image d'abord.")
        else:
            try:
                # Étape 1 : Trouver le modèle qui marche sur ton serveur
                target_model = get_working_model_name()
                model = genai.GenerativeModel(target_model)
                
                with st.spinner(f'🧠 Bakhana analyse avec {target_model}...'):
                    # Étape 2 : Envoyer le prompt
                    prompt = f"""
                    Analyse ce médicament. Donne :
                    1. NOM et USAGE.
                    2. DOSAGE.
                    3. PRÉCAUTION.
                    Réponds sans astérisques et de façon très courte.
                    Question patient : {user_query if user_query else "Analyse générale."}
                    """
                    
                    response = model.generate_content([prompt, Image.open(uploaded_file)])
                    
                if response.text:
                    # Nettoyage du texte pour l'affichage et la voix
                    clean_text = response.text.replace("*", "").replace("#", "")
                    st.write(clean_text)
                    
                    # Étape 3 : Génération de l'audio
                    try:
                        tts = gTTS(text=clean_text, lang='fr')
                        tts.save("speech.mp3")
                        st.audio("speech.mp3")
                    except Exception as e_audio:
                        st.warning("Lecture vocale indisponible.")
                else:
                    st.error("L'IA n'a pas pu générer de réponse.")
                    
            except Exception as e:
                st.error(f"Erreur technique : {e}")