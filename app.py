import os
import time
import json
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import paho.mqtt.client as paho

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Control por Voz",
    page_icon="🎙️",
    layout="wide"
)

# =========================
# ESTILOS CSS
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #eefbf3 0%, #e2f7ea 100%);
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #14532d;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #166534;
        margin-bottom: 1rem;
    }

    .card {
        background: white;
        padding: 1.4rem;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(22, 101, 52, 0.12);
        border: 1px solid #d1fae5;
        margin-bottom: 1rem;
    }

    .info-box {
        background: #ecfdf5;
        padding: 1rem;
        border-radius: 14px;
        border-left: 6px solid #22c55e;
        color: #14532d;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.10);
    }

    .result-box {
        background: #f0fdf4;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #86efac;
        color: #14532d;
        font-size: 1.05rem;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.12);
    }

    .small-note {
        color: #166534;
        font-size: 0.95rem;
    }

    .footer-box {
        background: #dcfce7;
        padding: 0.9rem 1rem;
        border-radius: 12px;
        color: #14532d;
        border: 1px solid #86efac;
        box-shadow: 0 3px 10px rgba(34, 197, 94, 0.10);
    }

    div.stButton > button {
        background: linear-gradient(90deg, #16a34a, #22c55e);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 6px 16px rgba(34, 197, 94, 0.22);
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #15803d, #16a34a);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: #f0fdf4;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNCIONES MQTT
# =========================
def on_publish(client, userdata, result):
    print("El dato ha sido publicado\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(1)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# =========================
# CONFIGURACIÓN MQTT
# =========================
# Ajustado para que coincida con tu código de Wokwi
broker = "157.230.214.127"
port = 1883
topic_envio = "cmqtt_a"

client1 = paho.Client("GIT-mmal")
client1.on_message = on_message

# =========================
# FUNCIÓN DE MAPEO DE VOZ
# =========================
def interpretar_comando(texto):
    texto = texto.lower().strip()

    if "nube" in texto:
        return {"Act1": "ON"}, "🟢 Se detectó la palabra 'nube' → comando ON"
    elif "salsa" in texto:
        return {"Act1": "OFF"}, "🔴 Se detectó la palabra 'salsa' → comando OFF"
    else:
        return None, "⚠️ No se detectó ni 'nube' ni 'salsa'."

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown(f"**Broker:** `{broker}`")
    st.markdown(f"**Puerto:** `{port}`")
    st.markdown(f"**Topic de envío:** `{topic_envio}`")

    st.markdown("---")
    st.markdown("## 🧭 Instrucciones")
    st.markdown("""
- Presiona el botón de inicio.
- Di claramente **nube** o **salsa**.
- La aplicación reconocerá tu voz.
- Si escucha **nube**, enviará `ON`.
- Si escucha **salsa**, enviará `OFF`.
    """)

    st.markdown("---")
    st.markdown("## 💡 Comandos válidos")
    st.markdown("- ☁️ **nube** → enciende")
    st.markdown("- 🌶️ **salsa** → apaga")

# =========================
# ENCABEZADO
# =========================
st.markdown('<div class="main-title">🎙️ Interfaces Multimodales</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🟢 Control por Voz con MQTT</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    Esta aplicación reconoce la voz del usuario y la convierte en comandos MQTT.
    En esta versión solo se admiten dos palabras clave:
    <strong>nube</strong> y <strong>salsa</strong>.
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================
# CONTENIDO PRINCIPAL
# =========================
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🖼️ Recurso visual")

    try:
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_container_width=True)
    except:
        st.warning("No se encontró la imagen `voice_ctrl.jpg` en el repositorio.")

    st.markdown(
        '<p class="small-note">Pronuncia una palabra clave para activar el comando correspondiente.</p>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎤 Activación del reconocimiento de voz")
    st.write("Haz clic en el botón y di una de estas dos palabras: **nube** o **salsa**.")

    stt_button = Button(label="🎙️ Iniciar reconocimiento", width=220)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "es-ES";

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
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
        texto_reconocido = result.get("GET_TEXT").strip()

        st.markdown("### ✅ Texto reconocido")
        st.markdown(
            f'<div class="result-box">🗣️ {texto_reconocido}</div>',
            unsafe_allow_html=True
        )

        payload, mensaje_estado = interpretar_comando(texto_reconocido)

        if payload is not None:
            client1.on_publish = on_publish
            client1.connect(broker, port)

            message = json.dumps(payload)
            client1.publish(topic_envio, message)

            st.success("📡 Mensaje enviado correctamente")
            st.info(mensaje_estado)
            st.code(message, language="json")
        else:
            st.warning(mensaje_estado)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PIE
# =========================
st.write("")
st.markdown("""
<div class="footer-box">
    ✅ <strong>Comportamiento esperado:</strong><br>
    ☁️ Si dices <strong>nube</strong>, la app enviará <code>{"Act1":"ON"}</code>.<br>
    🌶️ Si dices <strong>salsa</strong>, la app enviará <code>{"Act1":"OFF"}</code>.
</div>
""", unsafe_allow_html=True)

# =========================
# CREAR CARPETA TEMP
# =========================
try:
    os.mkdir("temp")
except:
    pass
