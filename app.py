import os
import streamlit as st
import base64
from openai import OpenAI

# === Función para codificar una imagen a base64 ===
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# === Configuración inicial de la página ===
st.set_page_config(page_title="Análisis de imagen 🤖🏞️", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen 🤖🏞️")

# === Campo para ingresar la clave de OpenAI ===
ke = st.text_input('Ingresa tu Clave', type="password")

if ke:
    os.environ['OPENAI_API_KEY'] = ke
else:
    st.warning("Por favor ingresa tu clave de OpenAI para continuar")

# Inicialización del cliente de OpenAI
api_key = os.environ.get('OPENAI_API_KEY')
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

# === Carga de imagen ===
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# === Toggle para añadir contexto o pregunta específica ===
show_details = st.toggle("¿Quieres preguntar algo específico sobre la imagen?", value=False)

if show_details:
    additional_details = st.text_area(
        "Agrega contexto o una pregunta específica sobre la imagen:",
        placeholder="Ejemplo: ¿Qué emociones transmite esta imagen?",
        disabled=not show_details
    )

# === Botón para analizar la imagen ===
analyze_button = st.button("Analizar imagen", type="secondary")

# === Lógica principal de análisis ===
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando la imagen..."):
        try:
            # Codificar la imagen en base64
            base64_image = encode_image(uploaded_file)
            prompt_text = "Describe brevemente en español lo que ves en la imagen."

            if show_details and additional_details:
                prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

            # Mensajes para el modelo multimodal
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]

            # Llamada al modelo GPT-4o
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Ocurrió un error al procesar la imagen: {e}")

else:
    # === Mensajes de advertencia ===
    if not uploaded_file and analyze_button:
        st.warning("Por favor, sube una imagen antes de analizar.")
    if not api_key:
        st.warning("Por favor, ingresa tu clave de API para continuar.")
