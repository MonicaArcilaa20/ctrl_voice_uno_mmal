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
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# =========================
# CONFIGURACIÓN MQTT
# =========================
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-mmal")
client1.on_message = on_message

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown(f"**Broker:** `{broker}`")
    st.markdown(f"**Puerto:** `{port}`")
    st.markdown("**Topic de envío:** `voice_ctrl_mmal`")

    st.markdown("---")
    st.markdown("## 🧭 Instrucciones")
    st.markdown("""
- Presiona el botón de inicio.
- Habla claramente al micrófono.
- La aplicación reconocerá tu voz.
- El texto capturado será enviado por MQTT.
    """)

    st.markdown("---")
    st.markdown("## 💡 Sugerencia")
    st.markdown("Usa comandos cortos y claros para obtener mejor reconocimiento.")

# =========================
# ENCABEZADO
# =========================
st.markdown('<div class="main-title">🎙️ Interfaces Multimodales</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🟢 Control por Voz con MQTT</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    Esta aplicación permite capturar una instrucción hablada, convertirla en texto
    y enviarla mediante <strong>MQTT</strong> al topic configurado.  
    Es una interfaz simple, visual y funcional para trabajar con comandos de voz.
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
        image = Image.open('voice_ctrl.jpg')
        st.image(image, use_container_width=True)
    except:
        st.warning("No se encontró la imagen `voice_ctrl.jpg` en el repositorio.")

    st.markdown(
        '<p class="small-note">La imagen acompaña visualmente el funcionamiento del control por voz.</p>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎤 Activación del reconocimiento de voz")
    st.write("Haz clic en el botón y habla. Cuando el sistema detecte tu voz, mostrará el texto reconocido y lo enviará automáticamente.")

    stt_button = Button(label="🎙️ Iniciar reconocimiento", width=220)

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

    if result:
        if "GET_TEXT" in result:
            texto_reconocido = result.get("GET_TEXT").strip()

            st.markdown("### ✅ Texto reconocido")
            st.markdown(
                f'<div class="result-box">🗣️ {texto_reconocido}</div>',
                unsafe_allow_html=True
            )

            client1.on_publish = on_publish
            client1.connect(broker, port)

            message = json.dumps({"Act1": texto_reconocido})
            ret = client1.publish("voice_ctrl_mmal", message)

            st.success("📡 Mensaje enviado correctamente al topic `voice_ctrl_mmal`")
            st.code(message, language="json")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PIE
# =========================
st.write("")
st.markdown("""
<div class="footer-box">
    ✅ <strong>Estado esperado:</strong> al hablar, la aplicación reconoce el texto y lo publica en MQTT.  
    🌿 Interfaz ajustada con enfoque funcional, limpia y visualmente más agradable.
</div>
""", unsafe_allow_html=True)

# =========================
# CREAR CARPETA TEMP
# =========================
try:
    os.mkdir("temp")
except:
    pass
