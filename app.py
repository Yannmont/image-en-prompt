import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="Prompt Studio & Pose Generator", layout="wide")
st.title("🎨 Prompt Studio & Générateur de Poses")
st.write("Téléversez une image pour obtenir son prompt précis, puis génerez 6 variantes de poses.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Entrez votre clé API Gemini :", type="password")

if not api_key:
    st.warning("⚠️ Veuillez entrer votre clé API Gemini dans la barre latérale pour commencer.")
    st.stop()

# Configuration de la clé
genai.configure(api_key=api_key)

st.header("1. Analyse de l'Image source")
uploaded_file = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])

if 'generated_prompt' not in st.session_state:
    st.session_state.generated_prompt = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(image, caption="Image source", use_container_width=True)
    
    with col2:
        st.subheader("📝 Prompt Précis Généré")
        if st.button("Analyser l'image"):
            with st.spinner("Analyse en cours par Gemini..."):
                try:
                    # Utilisation du modèle Flash pour l'analyse
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt_instruction = (
                        "Analyze this image in detail. Write an ultra-precise image generation prompt "
                        "in English. Include artistic style, subject details, colors, lighting, and atmosphere. "
                        "Provide ONLY the prompt text, nothing else."
                    )
                    response = model.generate_content([prompt_instruction, image])
                    st.session_state.generated_prompt = response.text
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {e}")

final_prompt = st.text_area("Modifier le prompt de base si nécessaire :", value=st.session_state.generated_prompt, height=150)

if final_prompt:
    st.write("---")
    st.header("2. Génération des 6 Variantes de Poses")
    
    poses = [
        "standing forward facing, full body portrait",
        "side profile view, dynamic posture",
        "action pose, running or jumping, mid-motion",
        "three-quarter view, sitting down thoughtfully",
        "dramatic hero shot, low angle looking up",
        "close-up portrait focusing on facial expression and upper body"
    ]
    
    if st.button("🚀 Générer les 6 variantes de pose"):
        st.write("Génération des images en cours...")
        cols = st.columns(3)
        
        # Changement ici : On utilise le modèle d'image natif de Gemini
        img_model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-image',
            generation_config={"response_modalities": ["IMAGE"]}
        )
        
        for i, pose in enumerate(poses):
            complete_prompt = f"Generate an image based on this description: {final_prompt}, {pose}, consistent character, high quality."
            with cols[i % 3]:
                st.subheader(f"Pose {i+1}")
                st.caption(f"Pose : {pose}")
                with st.spinner("Génération..."):
                    try:
                        # Demande de génération d'image
                        response = img_model.generate_content(complete_prompt)
                        
                        # Extraction et affichage de l'image reçue
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                img_bytes = io.BytesIO(part.inline_data.data)
                                img_to_show = Image.open(img_bytes)
                                st.image(img_to_show, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur de génération : {e}")
