import os
import streamlit as st
import base64
from openai import OpenAI

# Función para codificar la imagen en base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


# Configuración de la página
st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")

# Título
st.title("Análisis de Imagen:🤖🏞️")

# Entrada de clave API
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Recuperar la clave
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente OpenAI solo si hay clave
client = OpenAI(api_key=api_key) if api_key else None

# Subir imagen
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# Mostrar imagen cargada
if uploaded_file:
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle para contexto adicional
show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area(
        "Adiciona contexto de la imagen aqui:",
        disabled=not show_details
    )

# Botón de análisis
analyze_button = st.button("Analiza la imagen", type="secondary")

# Si hay imagen, clave y se presiona el botón
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        try:
            # Codificar la imagen
            base64_image = encode_image(uploaded_file)

            prompt_text = "Describe what you see in the image in spanish"

            if show_details and additional_details:
                prompt_text += f"\n\nAdditional Context Provided by the User:\n{additional_details}"

            # Mensajes para el modelo
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ]

            # Streaming de la respuesta
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

            # Mostrar respuesta final
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    # Advertencias al usuario
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
