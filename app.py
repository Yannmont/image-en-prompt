import streamlit as st
from google import genai

st.title("🔧 Diagnostic de la Clé API")

# 1. Est-ce que Streamlit voit le secret ?
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ Streamlit ne trouve AUCUN secret nommé GOOGLE_API_KEY.")
else:
    ma_cle = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ Streamlit trouve bien le secret.")
    
    # 2. Analyse visuelle de la clé (sécurisée)
    st.write(f"Longueur de votre clé : {len(ma_cle)} caractères")
    st.write(f"Elle commence par : `{ma_cle[:6]}`")
    st.write(f"Elle se termine par : `{ma_cle[-4:]}`")
    
    # 3. Test de validation en direct
    if not ma_cle.startswith("AIzaSy"):
        st.error("❌ Erreur critique : Une clé Gemini valide DOIT commencer par 'AIzaSy'.")

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
