import os
import streamlit as st
import base64
from openai import OpenAI

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Análisis de Imagen 🤖🏞️", layout="centered", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES PERSONALIZADOS ---
st.markdown("""
    <style>
        /* Fondo general suave */
        body {
            background-color: #f5f7fa;
        }
        /* Título centrado y elegante */
        h1 {
            text-align: center;
            color: #222831;
            font-family: 'Poppins', sans-serif;
            margin-bottom: 0.5em;
        }
        /* Subtítulos y textos */
        .stMarkdown p {
            font-family: 'Inter', sans-serif;
            color: #393e46;
        }
        /* Cuadro de carga */
        .upload-box {
            border: 2px dashed #00adb5;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #ffffff;
        }
        /* Botón */
        .stButton>button {
            background-color: #00adb5;
            color: white;
            border: none;
            padding: 0.7em 1.5em;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #007b83;
        }
        /* Área de texto */
        textarea {
            border-radius: 10px !important;
            border: 1.5px solid #00adb5 !important;
        }
        /* Caja de respuesta */
        .response-box {
            background-color: #e3fdfd;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #00adb5;
        }
    </style>
""", unsafe_allow_html=True)


# --- TÍTULO ---
st.title("🧠 Análisis de Imagen con Inteligencia Artificial")

st.markdown("""
Bienvenido a esta herramienta interactiva que analiza imágenes usando **modelos de OpenAI**.  
Sube una imagen, formula una pregunta y descubre cómo la IA interpreta lo que ve 👀.
""")

# --- API KEY ---
st.markdown("### 🔑 Conexión con OpenAI")
ke = st.text_input('Ingresa tu Clave de API', type='password', placeholder="sk-...")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY', None)

client = OpenAI(api_key=api_key) if api_key else None

# --- SUBIDA DE IMAGEN ---
st.markdown("### 🖼️ Carga tu imagen para analizar")
uploaded_file = st.file_uploader("Arrastra o selecciona una imagen (jpg, png, jpeg)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.markdown("#### Vista previa de la imagen:")
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True, output_format="auto")


# --- DETALLES ADICIONALES ---
st.markdown("### 💬 Contexto adicional (opcional)")
show_details = st.toggle("¿Quieres preguntar algo específico sobre la imagen?", value=False)

if show_details:
    additional_details = st.text_area(
        "Agrega tu pregunta o contexto aquí:",
        placeholder="Ejemplo: ¿Qué emociones transmite la persona en la imagen?",
        disabled=not show_details
    )
else:
    additional_details = ""

# --- BOTÓN DE ANÁLISIS ---
analyze_button = st.button("🔍 Analizar Imagen")

# --- LÓGICA DE ANÁLISIS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

if uploaded_file and api_key and analyze_button:
    with st.spinner("Analizando la imagen... 🔄"):
        try:
            base64_image = encode_image(uploaded_file)
            prompt_text = "Describe en español lo que ves en la imagen."

            if show_details and additional_details.strip():
                prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

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

            # Mostrar resultado con streaming
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(f"<div class='response-box'>{full_response}▌</div>", unsafe_allow_html=True)

            message_placeholder.markdown(f"<div class='response-box'>{full_response}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# --- MENSAJES DE ADVERTENCIA ---
elif analyze_button:
    if not uploaded_file:
        st.warning("⚠️ Por favor, sube una imagen antes de analizar.")
    if not api_key:
        st.warning("⚠️ Ingresa tu clave de API de OpenAI.")
