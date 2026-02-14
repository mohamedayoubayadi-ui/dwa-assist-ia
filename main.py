import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# 1. Configuration de la page
st.set_page_config(page_title="Bakhana - Dwa-Assist", page_icon="💊", layout="wide")

# Look épuré
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- RÉCUPÉRATION DE LA CLÉ API ---
try:
    # Récupère la clé depuis les Secrets de Streamlit Cloud
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("❌ Erreur : La clé API n'est pas configurée dans les Secrets de Streamlit.")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.success("✅ Bakhana est prêt")
    
    system_instruction = """
    Tu es Bakhana, l'assistant intelligent du projet Dwa-Assist. 
    Ton rôle est d'aider les personnes à comprendre leurs médicaments de manière simple et rassurante.
    """
    
    st.info("📸 Conseil : Assurez-vous que le texte sur la boîte est bien éclairé.")

# --- TITRE PRINCIPAL ---
st.title("💊 Bakhana : Dwa-Assist")
st.markdown("### Votre Pharmacien IA Intelligent (Vision & Voix 🗣️)")
st.markdown("---")

col1, col2 = st.columns([1, 1]) 

uploaded_file = st.sidebar.file_uploader("Charger la photo du médicament", type=["jpg", "png", "jpeg"])
image_data = None

# --- COLONNE GAUCHE (Image) ---
with col1:
    if uploaded_file:
        st.success("📸 Image reçue")
        image_data = Image.open(uploaded_file)
        st.image(image_data, use_column_width=True)
    else:
        st.info("👈 Veuillez charger une photo pour commencer l'analyse.")

# --- COLONNE DROITE (Analyse) ---
with col2:
    st.subheader("Analyse de Bakhana")
    user_prompt = st.text_area("Question optionnelle :", height=100, placeholder="Ex: Est-ce pour le rhume ?")
    
    if st.button("Analyser le médicament 🚀", type="primary", use_container_width=True):
        if not image_data:
            st.warning("⚠️ Merci d'ajouter une photo d'abord.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                with st.spinner('🧠 Bakhana analyse votre médicament...'):
                    # PROMPT CORRIGÉ (bien fermé avec """)
                    prompt_final = f"""
                    Analyse cette image de médicament.
                    Donne-moi UNIQUEMENT ces 3 points de manière très claire :
                    1. NOM et USAGE (À quoi sert ce médicament ?)
                    2. DOSAGE (Comment faut-il le prendre ?)
                    3. PRÉCAUTION (Y a-t-il un danger ou une contre-indication ?)
                    
                    Question du patient : {user_prompt if user_prompt else "Analyse générale."}
                    Réponds de façon concise et bienveillante.
                    """ 
                    
                    # Génération du contenu
                    response = model.generate_content([system_instruction, prompt_final, image_data])
                
                # Vérification et affichage du texte
                if response and response.text:
                    st.markdown("### 📋 Résultat :")
                    st.write(response.text)
                    
                    # GÉNÉRATION DE LA VOIX
                    try:
                        # On nettoie le texte pour la synthèse vocale
                        texte_propre = response.text.replace("*", "")
                        
                        tts = gTTS(text=texte_propre, lang='fr')
                        tts.save("output_bakhana.mp3")
                        
                        st.audio("output_bakhana.mp3")
                        st.success("🗣️ Analyse vocale disponible.")
                    except Exception as e_audio:
                        st.error(f"Erreur lors de la création du son : {e_audio}")
                else:
                    st.error("L'IA n'a pas pu générer de réponse. Réessayez avec une image plus claire.")

            except Exception as e:
                st.error(f"Erreur technique : {e}")