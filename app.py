import streamlit as st
from google import genai
from google.genai import types
from PIL import Image  # <-- Cette ligne cruciale manquait et causait le crash !
import io

# Configuration de l'interface Streamlit
st.set_page_config(page_title="Studio Image - Banana API", page_icon="🍌", layout="centered")
st.title("🍌 Banana Image Studio")
st.write("Générez et modifiez vos images nativement avec l'API Gemini")

# Vérification de la clé API dans les Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ La clé GOOGLE_API_KEY n'est pas configurée dans les Secrets de Streamlit.")
    st.stop()

# Initialisation du client officiel Google GenAI
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
MODEL_NAME = "gemini-3.1-flash-image-preview"

# Création des onglets
tab1, tab2 = st.tabs(["✨ Générer une image", "🛠️ Modifier une image"])

# --- ONGLET 1 : GÉNÉRATION TEXT-TO-IMAGE ---
with tab1:
    st.subheader("Créer un visuel à partir d'un texte")
    prompt_gen = st.text_area(
        "Décrivez l'image que vous souhaitez créer :", 
        placeholder="Un astronaute chevauchant un cheval sur Mars...",
        key="prompt_gen"
    )
    
    ratio = st.selectbox(
        "Format de l'image :",
        options=["16:9", "1:1", "4:3", "9:16"],
        index=1
    )
    
    if st.button("Créer le visuel", type="primary", key="btn_gen"):
        if not prompt_gen.strip():
            st.warning("Veuillez écrire une description.")
        else:
            with st.spinner("Génération en cours..."):
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt_gen,
                        config=types.GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"],
                            image_config=types.ImageConfig(aspect_ratio=ratio, image_size="1K"),
                        )
                    )
                    
                    image_affichee = False
                    for part in response.parts:
                        if image_data := part.as_image():
                            st.image(image_data, caption="Résultat de la génération", use_container_width=True)
                            image_affichee = True
                    
                    if not image_affichee:
                        st.error("Le modèle n'a pas renvoyé d'image.")
                except Exception as e:
                    st.error(f"Erreur API : {e}")

# --- ONGLET 2 : MODIFICATION IMAGE-TO-IMAGE ---
with tab2:
    st.subheader("Modifier une image existante")
    uploaded_file = st.file_uploader("Choisissez une image source...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        input_image = Image.open(uploaded_file)
        st.image(input_image, caption="Image source", width=300)
        
        prompt_edit = st.text_area(
            "Indiquez la modification à faire :",
            placeholder="Ajoute des lunettes de soleil / Change le fond pour une plage...",
            key="prompt_edit"
        )
        
        if st.button("Appliquer la modification", type="primary", key="btn_edit"):
            if not prompt_edit.strip():
                st.warning("Veuillez donner une instruction.")
            else:
                with st.spinner("Modification en cours..."):
                    try:
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=[
                                f"Modifie cette image selon l'instruction suivante : {prompt_edit}",
                                input_image
                            ],
                            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
                        )
                        
                        image_affichee = False
                        for part in response.parts:
                            if image_data := part.as_image():
                                st.image(image_data, caption="Image modifiée", use_container_width=True)
                                image_affichee = True
                        
                        if not image_affichee:
                            st.error("Le modèle n'a pas pu appliquer la modification.")
                    except Exception as e:
                        st.error(f"Erreur API : {e}")
