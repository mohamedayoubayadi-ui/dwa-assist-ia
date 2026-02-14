import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS 
import os

# Configuration de la page
st.set_page_config(page_title="Dwa-Assist", page_icon="💊", layout="wide")

# CSS pour le look pro
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- Barre latérale ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    api_key = st.text_input("Clé API Google :", type="password")
    
    # --- MODIFICATION 1 : LE CERVEAU ---
    system_instruction = """
    Tu es Dwa-Assist, un pharmacien virtuel expert.
    Ton but est de sécuriser la prise de médicaments pour les patients.
    Tu parles lentement et clairement.
    """

# --- TITRE ---
st.title("💊 Dwa-Assist")
st.markdown("### Votre Pharmacien IA (Vision & Voix 🗣️)")
st.markdown("---")

# Colonnes
col1, col2 = st.columns([1, 1]) 

uploaded_file = st.sidebar.file_uploader("Prendre une photo du médicament", type=["jpg", "png", "jpeg"])
image_data = None

# --- Colonne Gauche (Vision) ---
with col1:
    if uploaded_file:
        st.success("📸 Médicament détecté")
        image_data = Image.open(uploaded_file)
        st.image(image_data, use_column_width=True)
    else:
        st.info("👈 Chargez une photo de la boîte ou de l'ordonnance.")

# --- Colonne Droite (Cerveau) ---
with col2:
    st.subheader("Analyse du Pharmacien")
    # On laisse le champ vide par défaut car l'IA va travailler seule
    user_prompt = st.text_area("Question spécifique (Optionnel) :", height=100)
    
    # BOUTON D'ENVOI
    if st.button("Analyser le médicament 💊", type="primary", use_container_width=True):
        if not api_key:
            st.error("⚠️ Veuillez entrer la Clé API à gauche.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                
                with st.spinner('💊 Dwa-Assist analyse la boîte...'):
                    
                    # --- MODIFICATION 2 : LE PROMPT FORCÉ ---
                    if image_data:
                        # C'est ici la magie : On force la structure de réponse
                        prompt_pharmacien = """
                        Analyse cette image de médicament.
                        Donne-moi UNIQUEMENT ces 3 informations sous forme de liste très courte :
                        1. 💊 NOM et USAGE : (Ex: Doliprane, pour la douleur)
                        2. 🥄 DOSAGE STANDARD : (Ex: 1 comprimé toutes les 6h)
                        3. ⚠️ ATTENTION : (Ex: Ne pas dépasser 3g/jour)
                        
                        Réponds comme si tu parlais à une personne âgée : sois rassurant, clair et concis.
                        """
                        response = model.generate_content([system_instruction, prompt_pharmacien, image_data])
                    else:
                        # Si pas d'image, on discute juste
                        response = model.generate_content(f"{system_instruction}\n\nQuestion patient : {user_prompt}")
                
                # Affichage du texte
                st.success("Analyse terminée !")
                st.markdown("### 📋 Résultat :")
                st.write(response.text)
                
                # Génération de la voix
# 3. GÉNÉRATION DE LA VOIX
                try:
                    # --- CORRECTION ICI ---
                    # On enlève les étoiles (*) pour que la voix ne les lise pas
                    texte_propre = response.text.replace("*", "") 
                    
                    tts = gTTS(text=texte_propre, lang='fr')
                    tts.save("reponse_pharma.mp3")
                    st.audio("reponse_pharma.mp3")
                    st.success("🗣️ Lecture audio activée")
                    
                except Exception as e_audio:
                    st.warning(f"Pas de son : {e_audio}")
            except Exception as e:
                st.error(f"Erreur : {e}")