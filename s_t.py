import os
import glob
import time
from PIL import Image

import streamlit as st
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
from googletrans import Translator

# --- Configuración de la página ---
st.set_page_config(
    page_title="Traductor Inteligente", 
    page_icon="🌐", 
    layout="centered"
)

# --- Estilos CSS personalizados ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    .gradient-header {
        background: linear-gradient(90deg, #4a8cff 0%, #6c5ce7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    .feature-card {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #4a8cff;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        border-radius: 12px;
        height: 50px;
        width: 100%;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(74, 140, 255, 0.2);
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(74, 140, 255, 0.3);
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-radius: 12px;
        padding: 16px;
        color: #155724;
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        border-radius: 12px;
        padding: 16px;
        color: #0c5460;
    }
    
    .recording-button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Encabezado mejorado ---
col1, col2 = st.columns([1, 3])
with col1:
    try:
        image = Image.open('OIG7.jpg')
        st.image(image, width=120)
    except:
        st.markdown("<div style='text-align: center; font-size: 80px;'>🌐</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<h1 class="gradient-header">Traductor Inteligente</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 18px; color: #6c757d;">🎙️ Habla y deja que traduzca por ti</p>', unsafe_allow_html=True)

st.markdown("---")

# --- Sección de grabación mejorada ---
st.markdown('<div class="feature-card">', unsafe_allow_html=True)
st.markdown("### 🎤 Toca el botón y habla lo que quieres traducir")

# Botón de grabación corregido
stt_button = Button(
    label="🎤 Iniciar Grabación", 
    width=300, 
    height=60,
    button_type="success"
)

stt_button.js_on_event("button_click", CustomJS(code="""
var recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;

recognition.onresult = function (e) {
    var value = "";
    for (var i = e.resultIndex; i < e.results.length; ++i) {
        if (e.results[i].isFinal) {
            value += e.results[i][0].transcript;
        }
    }
    if ( value != "") {
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
    }
}
recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=85,
    debounce_time=0
)

st.markdown('</div>', unsafe_allow_html=True)

# --- Mostrar el texto reconocido ---
if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Texto Reconocido:")
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Crear carpeta temporal
    os.makedirs("temp", exist_ok=True)

    # --- Configuración de idiomas mejorada ---
    translator = Translator()
    LANGUAGES = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }

    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Configuración de Traducción")
    
    col1, col2 = st.columns(2)
    with col1:
        in_lang = st.selectbox(
            "**Idioma de Entrada**", 
            list(LANGUAGES.keys()),
            help="Selecciona el idioma en el que estás hablando"
        )
    with col2:
        out_lang = st.selectbox(
            "**Idioma de Salida**", 
            list(LANGUAGES.keys()),
            help="Selecciona el idioma al que quieres traducir"
        )
    
    # --- Selección de acento mejorada ---
    ACCENTS = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    
    tld = st.selectbox(
        "**Acento del habla**", 
        list(ACCENTS.keys()),
        help="Selecciona el acento para la voz generada"
    )
    tld = ACCENTS[tld]
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Función de conversión ---
    def text_to_speech(input_lang, output_lang, text, tld):
        translation = translator.translate(text, src=input_lang, dest=output_lang)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_lang, tld=tld, slow=False)
        safe_name = "".join(c for c in text[:20] if c.isalnum()) or "audio"
        file_path = f"temp/{safe_name}.mp3"
        tts.save(file_path)
        return file_path, trans_text

    display_text = st.checkbox("Mostrar texto traducido", value=True)

    # --- Botón convertir mejorado ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔊 Convertir y Reproducir", type="primary", use_container_width=True):
            with st.spinner("🔄 Traduciendo y generando audio..."):
                audio_file, translated_text = text_to_speech(LANGUAGES[in_lang], LANGUAGES[out_lang], text, tld)
                
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown("### 🔊 Audio Generado")
                st.audio(audio_file, format="audio/mp3")
                
                if display_text:
                    st.markdown("### 📖 Texto Traducido:")
                    st.markdown(f'<div class="success-box">{translated_text}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # --- Limpieza de archivos antiguos ---
    def remove_old_files(days=7):
        for f in glob.glob("temp/*.mp3"):
            if time.time() - os.stat(f).st_mtime > days * 86400:
                os.remove(f)
    remove_old_files()

# --- Pie de página mejorado ---
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #6c757d; font-size: 14px;">'
    'Traductor Inteligente • Hecho con Streamlit'
    '</div>', 
    unsafe_allow_html=True
)
