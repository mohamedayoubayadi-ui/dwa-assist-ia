import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de la page
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# Cache le menu Streamlit
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- RÉCUPÉRATION DE LA CLÉ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("❌ Erreur : Configurez GOOGLE_API_KEY dans les Secrets de Streamlit.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.success("✅ Bakhana est prêt")
    system_instruction = "Tu es Bakhana, un assistant pharmacien intelligent et bienveillant."
    uploaded_file = st.file_uploader("Charger la photo du médicament", type=["jpg", "png", "jpeg"])

# --- TITRE ---
st.title("💊 Bakhana : Dwa-Assist")
st.markdown("### Votre Pharmacien IA Intelligent (Vision & Voix 🗣️)")
st.markdown("---")

col1, col2 = st.columns([1, 1]) 

# --- COLONNE GAUCHE ---
with col1:
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, use_column_width=True)
    else:
        st.info("👈 Chargez une photo pour commencer.")

# --- COLONNE DROITE ---
with col2:
    st.subheader("Analyse de Bakhana")
    user_prompt = st.text_area("Question ?", placeholder="Ex: C'est pour le mal de tête ?")
    
    if st.button("Analyser 🚀", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Ajoutez une photo d'abord.")
        else:
            try:
                genai.configure(api_key=api_key)
                # Utilisation du nom de modèle le plus compatible
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                with st.spinner('🧠 Analyse en cours...'):
                    prompt_final = f"""
                    Analyse cette image. Donne :
                    1. NOM et USAGE
                    2. DOSAGE
                    3. PRÉCAUTION
                    Question patient : {user_prompt if user_prompt else "Analyse générale."}
                    Réponds de façon courte.
                    """ 
                    
                    # On repasse l'image ouverte
                    img = Image.open(uploaded_file)
                    response = model.generate_content([system_instruction, prompt_final, img])
                
                if response and response.text:
                    st.markdown("### 📋 Résultat :")
                    st.write(response.text)
                    
                    # AUDIO
                    try:
                        clean_text = response.text.replace("*", "")
                        tts = gTTS(text=clean_text, lang='fr')
                        tts.save("bakhana_audio.mp3")
                        st.audio("bakhana_audio.mp3")
                    except Exception as e_audio:
                        st.warning("Son indisponible.")
                else:
                    st.error("Pas de réponse de l'IA.")

            except Exception as e:
                st.error(f"Erreur technique : {e}")