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
    page_title="Traductor", 
    page_icon="🎙️", 
    layout="centered"
)

# --- Estilos CSS personalizados ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
    }
    
    .bokeh-button-container {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .bokeh-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 8px 16px rgba(255, 107, 107, 0.5) !important;
        transition: all 0.3s ease !important;
        width: 350px !important;
        height: 80px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    .bokeh-button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 24px rgba(255, 107, 107, 0.7) !important;
        background: linear-gradient(135deg, #ff5252 0%, #e84118 100%) !important;
    }
    
    /* Eliminar espacios blancos y fondos del botón de bokeh */
    .bk-root {
        background: transparent !important;
    }
    
    .bk-canvas {
        background: transparent !important;
    }
    
    div[data-testid="stBokehEvents"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    div[data-testid="stBokehEvents"] > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-radius: 12px;
        padding: 20px;
        color: #155724;
        font-size: 16px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 1px solid #90caf9;
        border-radius: 12px;
        padding: 20px;
        color: #0d47a1;
        font-size: 16px;
    }
    
    .stButton>button {
        border-radius: 15px;
        height: 60px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 6px 12px rgba(74, 140, 255, 0.3);
        border: none;
        font-size: 18px;
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(74, 140, 255, 0.4);
        background: linear-gradient(135deg, #218838 0%, #1e9e8a 100%);
    }
</style>
""", unsafe_allow_html=True)

# --- Botón de grabación ---
st.markdown('<div class="bokeh-button-container">', unsafe_allow_html=True)

stt_button = Button(
    label="🎤 INICIAR GRABACIÓN", 
    width=350, 
    height=80,
    button_type="success",
    css_classes=["bokeh-button"]
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
    override_height=90,
    debounce_time=0
)

st.markdown('</div>', unsafe_allow_html=True)

# --- Mostrar el texto reconocido ---
if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.markdown("**Texto reconocido:**")
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)

    # Crear carpeta temporal
    os.makedirs("temp", exist_ok=True)

    # --- Configuración de idiomas ---
    translator = Translator()
    LANGUAGES = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }

    col1, col2 = st.columns(2)
    with col1:
        in_lang = st.selectbox("Idioma de Entrada", list(LANGUAGES.keys()))
    with col2:
        out_lang = st.selectbox("Idioma de Salida", list(LANGUAGES.keys()))
    
    # --- Selección de acento ---
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
    
    tld = ACCENTS[st.selectbox("Acento del habla", list(ACCENTS.keys()))]

    # --- Función de conversión ---
    def text_to_speech(input_lang, output_lang, text, tld):
        translation = translator.translate(text, src=input_lang, dest=output_lang)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_lang, tld=tld, slow=False)
        safe_name = "".join(c for c in text[:20] if c.isalnum()) or "audio"
        file_path = f"temp/{safe_name}.mp3"
        tts.save(file_path)
        return file_path, trans_text

    display_text = st.checkbox("Mostrar texto traducido")

    # --- Botón convertir ---
    if st.button("🔊 Convertir", type="primary"):
        audio_file, translated_text = text_to_speech(LANGUAGES[in_lang], LANGUAGES[out_lang], text, tld)
        st.audio(audio_file, format="audio/mp3")
        if display_text:
            st.markdown("**Texto traducido:**")
            st.markdown(f'<div class="success-box">{translated_text}</div>', unsafe_allow_html=True)

    # --- Limpieza de archivos antiguos ---
    def remove_old_files(days=7):
        for f in glob.glob("temp/*.mp3"):
            if time.time() - os.stat(f).st_mtime > days * 86400:
                os.remove(f)
    remove_old_files()
