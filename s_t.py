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
st.set_page_config(page_title="Traductor Inteligente", page_icon="🌐", layout="centered")

# --- Título y descripción ---
st.title("🌐 Traductor Inteligente")
st.subheader("🎙️ Habla y deja que traduzca por ti")

# --- Imagen decorativa ---
image = Image.open('OIG7.jpg')
st.image(image, width=300)

# --- Barra lateral ---
with st.sidebar:
    st.header("Instrucciones")
    st.write(
        "1️⃣ Presiona el botón **Escuchar**.\n"
        "2️⃣ Habla lo que deseas traducir.\n"
        "3️⃣ Selecciona el idioma de entrada y salida.\n"
        "4️⃣ Escoge el acento y presiona **Convertir**."
    )

st.markdown("---")

# --- Botón de grabación ---
st.markdown("## Toca el botón y habla lo que quieres traducir")
stt_button = Button(label="🎤 Escuchar", width=250, height=50, button_type="success")

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
    override_height=75,
    debounce_time=0
)

# --- Mostrar el texto reconocido ---
if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.markdown(f"### Texto reconocido:")
    st.info(text)

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
            st.markdown(f"### Texto traducido:")
            st.success(translated_text)

    # --- Limpieza de archivos antiguos ---
    def remove_old_files(days=7):
        for f in glob.glob("temp/*.mp3"):
            if time.time() - os.stat(f).st_mtime > days * 86400:
                os.remove(f)
    remove_old_files()
