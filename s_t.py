import streamlit as st
from PIL import Image
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# --- Configuración de página ---
st.set_page_config(page_title="Traductor Inteligente", page_icon="🌐", layout="centered")

# --- Estilos personalizados ---
st.markdown("""
<style>
/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    color: #333;
    font-family: 'Arial', sans-serif;
}

/* Encabezados */
h1, h2, h3 {
    color: #222;
}

/* Botones */
.bk-root .bk-btn {
    background-color: #ff7f50 !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 18px !important;
    border-radius: 12px !important;
    height: 50px !important;
    width: 250px !important;
}

/* Caja de texto reconocida */
.stAlert {
    border-radius: 12px !important;
    background-color: #fff3e6 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Título ---
st.title("🌐 Traductor Inteligente")
st.subheader("Habla y deja que traduzca por ti")

# --- Imagen de cabecera ---
image = Image.open("58.png")
st.image(image, width=350)

st.markdown("## Toca el botón y habla lo que quieres traducir")

# --- Botón Hablar 🎤 ---
stt_button = Button(label="Hablar", width=250, height=50, button_type="success")

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

if result and "GET_TEXT" in result:
    st.success(f"📝 Texto reconocido: {result.get('GET_TEXT')}")
