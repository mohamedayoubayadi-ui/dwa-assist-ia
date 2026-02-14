import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de la page
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# Masquer les éléments inutiles
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- RÉCUPÉRATION DE LA CLÉ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("❌ Erreur : Clé 'GOOGLE_API_KEY' manquante dans les Secrets Streamlit.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.success("✅ Bakhana est prêt")
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
    user_prompt = st.text_area("Question spécifique ?", placeholder="Ex: Est-ce pour la douleur ?")
    
    if st.button("Lancer l'analyse 🚀", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Veuillez charger une photo.")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # --- SOLUTION ANTI-404 ---
                # On essaie d'utiliser 'gemini-1.5-flash', sinon on prend le premier disponible
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                except:
                    model = genai.GenerativeModel('gemini-pro-vision') 

                with st.spinner('🧠 Bakhana examine le médicament...'):
                    prompt_final = f"""
                    Analyse cette image de médicament.
                    Donne UNIQUEMENT ces 3 points de manière très claire :
                    1. NOM et USAGE
                    2. DOSAGE
                    3. PRÉCAUTION
                    
                    Note : {user_prompt if user_prompt else "Analyse générale."}
                    Réponds de façon concise et douce.
                    """ 
                    
                    img = Image.open(uploaded_file)
                    response = model.generate_content([system_instruction, prompt_final, img])
                
                if response and response.text:
                    # Nettoyage immédiat du texte pour l'affichage et l'audio
                    # On retire les symboles Markdown pour éviter que l'audio les lise
                    final_text = response.text.replace("*", "").replace("#", "")
                    
                    st.markdown("### 📋 Résultat :")
                    st.write(final_text)
                    
                    # GÉNÉRATION AUDIO
                    try:
                        tts = gTTS(text=final_text, lang='fr')
                        tts.save("audio_bakhana.mp3")
                        st.audio("audio_bakhana.mp3")
                        st.success("🗣️ Lecture vocale prête.")
                    except Exception as e_audio:
                        st.warning("Lecture vocale indisponible.")
                else:
                    st.error("L'IA n'a pas pu traiter l'image.")

            except Exception as e:
                st.error(f"Désolé, une erreur technique est survenue : {e}")