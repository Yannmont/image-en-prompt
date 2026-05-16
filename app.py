import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configuration de la page Streamlit
st.set_page_config(page_title="Prompt Studio & Pose Generator", layout="wide")
st.title("🎨 Prompt Studio & Générateur de Poses")
st.write("Téléversez une image pour obtenir son prompt précis, puis générez 6 variantes de poses.")

# --- CONFIGURATION API ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Entrez votre clé API Gemini :", type="password")
    if api_key:
        genai.configure(api_key=api_key)

if not api_key:
    st.warning("⚠️ Veuillez entrer votre clé API Gemini dans la barre latérale pour commencer.")
    st.stop()

# --- ETAPE 1 : ANALYSE DE L'IMAGE ---
st.header("1. Analyse de l'Image source")
uploaded_file = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])

generated_prompt = ""

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
                    model = genai.GenerativeModel('gemini-3-flash')
                    prompt_instruction = (
                        "Analyse cette image en détail. Rédige un prompt de génération d'image "
                        "ultra-précis en anglais. Inclus le style artistique, les détails du personnage/sujet, "
                        "les couleurs, l'éclairage et l'atmosphère. Ne donne QUE le prompt, rien d'autre."
                    )
                    response = model.generate_content([prompt_instruction, image])
                    generated_prompt = response.text
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {e}")

final_prompt = st.text_area("Modifier le prompt de base si nécessaire :", value=generated_prompt, height=150)

# --- ETAPE 2 : GENERATION DES VARIANTES ---
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
        imagen_model = genai.GenerativeModel('imagen-3.0-generate-002')
        
        for i, pose in enumerate(poses):
            complete_prompt = f"{final_prompt}, {pose}, consistent character, high quality."
            with cols[i % 3]:
                st.subheader(f"Pose {i+1}")
                st.caption(f"Pose : {pose}")
                with st.spinner("Génération..."):
                    try:
                        result = imagen_model.generate_images(
                            prompt=complete_prompt,
                            number_of_images=1,
                            aspect_ratio="1:1"
                        )
                        for generated_img in result.generated_images:
                            image_bytes = io.BytesIO(generated_img.image.image_bytes)
                            img_to_show = Image.open(image_bytes)
                            st.image(img_to_show, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur de génération : {e}")
