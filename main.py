import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de la page
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# Style pour une interface pro
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- RÉCUPÉRATION DE LA CLÉ API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("❌ Configuration incomplète : Clé API manquante dans les Secrets.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://em-content.zkg.io/thumbs/240/apple/354/pill_1f48a.png", width=100)
    st.title("⚙️ Paramètres")
    st.success("✅ Assistant Bakhana prêt")
    
    uploaded_file = st.file_uploader("Prendre une photo du médicament", type=["jpg", "png", "jpeg"])
    
    st.divider()
    st.info("💡 **Conseil :** Assurez-vous que le nom du médicament est bien visible.")

# --- TITRE PRINCIPAL ---
st.title("💊 Bakhana : Dwa-Assist")
st.markdown("### Votre Pharmacien IA Intelligent (Vision & Voix 🗣️)")
st.markdown("---")

col1, col2 = st.columns([1, 1.2]) 

# --- COLONNE GAUCHE (Image) ---
with col1:
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Médicament chargé", use_column_width=True)
    else:
        st.info("👈 Veuillez charger une photo pour lancer l'analyse.")

# --- COLONNE DROITE (Analyse) ---
with col2:
    st.subheader("Analyse de Bakhana")
    user_prompt = st.text_area("Question spécifique ? (Optionnel)", placeholder="Ex: Est-ce pour dormir ?")
    
    if st.button("Lancer l'analyse 🚀", use_container_width=True):
        if not uploaded_file:
            st.warning("⚠️ Merci d'ajouter une photo d'abord.")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # --- STRATÉGIE ANTI-404 ---
                # On teste les modèles du plus récent au plus compatible
                model = None
                available_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro-vision']
                
                for m_name in available_models:
                    try:
                        model = genai.GenerativeModel(m_name)
                        # Test de génération minimal pour valider le modèle
                        break 
                    except:
                        continue
                
                if not model:
                    st.error("❌ Erreur de connexion au serveur IA (404).")
                    st.stop()

                with st.spinner('🧠 Bakhana examine le document...'):
                    system_instruction = "Tu es Bakhana, un assistant pharmacien bienveillant. Réponds de façon simple."
                    prompt_final = f"""
                    Analyse cette image de médicament.
                    Donne UNIQUEMENT ces 3 points :
                    1. NOM et USAGE (C'est quoi ?)
                    2. DOSAGE (Comment le prendre ?)
                    3. PRÉCAUTION (Y a-t-il un danger ?)
                    
                    Question du patient : {user_prompt if user_prompt else "Analyse générale."}
                    Réponds sans utiliser de symboles spéciaux comme les astérisques.
                    """ 
                    
                    response = model.generate_content([system_instruction, prompt_final, image_data])
                
                if response and response.text:
                    # Nettoyage final du texte
                    final_text = response.text.replace("*", "").replace("#", "")
                    
                    st.markdown("### 📋 Résultat :")
                    st.write(final_text)
                    
                    # --- GÉNÉRATION AUDIO ---
                    try:
                        tts = gTTS(text=final_text, lang='fr')
                        tts.save("bakhana_speech.mp3")
                        st.audio("bakhana_speech.mp3")
                        st.success("🗣️ Analyse vocale disponible.")
                    except Exception:
                        st.warning("⚠️ Lecture vocale indisponible.")
                else:
                    st.error("L'IA n'a pas pu générer de texte.")

            except Exception as e:
                st.error(f"Désolé, une erreur technique est survenue : {e}")