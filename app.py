import os
import re
import json
import time
import streamlit as st
from PIL import Image
import paho.mqtt.client as mqtt
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Syntax Voice Control",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_BROKER = "157.230.214.127"
DEFAULT_PORT = 1883
DEFAULT_TOPIC_DIGITAL = "cmqtt_a"
DEFAULT_TOPIC_SERVO = "cmqtt_s"

# =========================================================
# ESTADO DE SESIÓN
# =========================================================
if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""

if "command_input" not in st.session_state:
    st.session_state.command_input = ""

if "last_payload" not in st.session_state:
    st.session_state.last_payload = {}

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

if "publish_status" not in st.session_state:
    st.session_state.publish_status = ""

# =========================================================
# ESTILOS
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.12), transparent 24%),
            radial-gradient(circle at top right, rgba(236,72,153,0.10), transparent 20%),
            radial-gradient(circle at bottom left, rgba(16,185,129,0.10), transparent 20%),
            linear-gradient(180deg, #0b1020 0%, #10182d 45%, #0f172a 100%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10,15,30,0.96) 0%, rgba(15,23,42,0.98) 100%);
        border-right: 1px solid rgba(148,163,184,0.18);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-size: 0.92rem !important;
    }

    [data-testid="stSidebar"] label {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(148,163,184,0.18) !important;
    }

    h1, h2, h3, p, li, label {
        color: #e5e7eb !important;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.92) 0%, rgba(30,41,59,0.92) 100%);
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 22px;
        padding: 28px 30px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.28);
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }

    .hero-title {
        font-size: 2.55rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin-bottom: 0.25rem;
        letter-spacing: -0.03em;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1 !important;
        margin-bottom: 0.8rem;
    }

    .hero-note {
        font-size: 0.94rem;
        color: #94a3b8 !important;
        line-height: 1.7;
    }

    .glass-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.88) 0%, rgba(17,24,39,0.88) 100%);
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 18px;
        padding: 22px 22px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.22);
        margin-bottom: 16px;
        backdrop-filter: blur(8px);
    }

    .section-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin-bottom: 0.8rem;
        letter-spacing: 0.01em;
    }

    .mini-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #cbd5e1 !important;
        margin-bottom: 0.55rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .chip {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        margin: 0 8px 8px 0;
        font-size: 0.83rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
    }

    .python { background: rgba(55,118,171,0.18); color: #93c5fd; }
    .json   { background: rgba(249,115,22,0.16); color: #fdba74; }
    .mqtt   { background: rgba(16,185,129,0.18); color: #6ee7b7; }
    .cpp    { background: rgba(168,85,247,0.18); color: #d8b4fe; }
    .esp32  { background: rgba(236,72,153,0.16); color: #f9a8d4; }

    .code-box {
        background: #0b1220;
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 14px;
        padding: 14px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #d1d5db;
        line-height: 1.7;
        white-space: pre-wrap;
        overflow-wrap: break-word;
    }

    .status-ok {
        background: rgba(16,185,129,0.12);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 12px 14px;
        color: #d1fae5 !important;
        margin-top: 10px;
    }

    .status-warn {
        background: rgba(245,158,11,0.12);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 12px 14px;
        color: #fde68a !important;
        margin-top: 10px;
    }

    .status-info {
        background: rgba(59,130,246,0.12);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 12px 14px;
        color: #bfdbfe !important;
        margin-top: 10px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 0 !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 0.72rem 1rem !important;
        background: linear-gradient(90deg, #7c3aed 0%, #2563eb 45%, #06b6d4 100%) !important;
        box-shadow: 0 10px 24px rgba(37,99,235,0.24) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(37,99,235,0.30) !important;
    }

    [data-testid="stDownloadButton"] button,
    [data-baseweb="select"] > div,
    textarea, input[type="text"], input[type="number"] {
        border-radius: 12px !important;
    }

    textarea, input[type="text"], input[type="number"] {
        background: rgba(15,23,42,0.95) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
    }

    [data-baseweb="select"] > div {
        background: rgba(15,23,42,0.95) !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
    }

    [data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(17,24,39,0.95) 100%);
        border: 1px solid rgba(148,163,184,0.16);
        border-top: 4px solid #38bdf8;
        border-radius: 16px;
        padding: 18px 18px;
        box-shadow: 0 10px 26px rgba(0,0,0,0.22);
    }

    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }

    .placeholder-visual {
        height: 220px;
        border-radius: 18px;
        border: 1px dashed rgba(148,163,184,0.26);
        background:
            radial-gradient(circle at 25% 25%, rgba(124,58,237,0.20), transparent 18%),
            radial-gradient(circle at 72% 30%, rgba(6,182,212,0.18), transparent 18%),
            radial-gradient(circle at 50% 75%, rgba(16,185,129,0.16), transparent 20%),
            linear-gradient(180deg, rgba(15,23,42,0.72) 0%, rgba(17,24,39,0.72) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #cbd5e1;
        font-weight: 700;
        text-align: center;
        padding: 16px;
    }

    .hint-card {
        background: rgba(15,23,42,0.7);
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .hint-card strong {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNCIONES
# =========================================================
def create_mqtt_client():
    client_id = f"syntax-ui-{int(time.time()*1000)}"
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
    except Exception:
        try:
            return mqtt.Client(client_id=client_id)
        except TypeError:
            return mqtt.Client(client_id)

def publish_payload(broker, port, topic, payload):
    client = create_mqtt_client()
    try:
        client.connect(broker, port, 60)
        info = client.publish(topic, json.dumps(payload))
        client.disconnect()
        if info.rc == 0:
            return True, f"Mensaje enviado a {topic}"
        return False, f"No se pudo publicar. Código MQTT: {info.rc}"
    except Exception as e:
        return False, f"Error de conexión/publicación: {e}"

def interpret_command(command_text):
    text = command_text.strip()
    text_lower = text.lower()

    # ON / OFF
    if any(word in text_lower for word in ["encender", "prender", "activar", "on"]):
        return {"Act1": "ON"}, "digital", "Comando digital detectado: encender."

    if any(word in text_lower for word in ["apagar", "desactivar", "off"]):
        return {"Act1": "OFF"}, "digital", "Comando digital detectado: apagar."

    # Servo semántico
    if any(word in text_lower for word in ["abrir", "maximo", "máximo", "full", "completo"]):
        return {"Analog": 100}, "servo", "Comando servo detectado: apertura máxima."

    if any(word in text_lower for word in ["centro", "medio", "mitad"]):
        return {"Analog": 50}, "servo", "Comando servo detectado: posición media."

    if any(word in text_lower for word in ["cerrar", "minimo", "mínimo"]):
        return {"Analog": 1}, "servo", "Comando servo detectado: cierre mínimo."

    # Número 0–100
    numbers = re.findall(r"\d+", text_lower)
    if numbers:
        value = max(0, min(100, int(numbers[0])))
        # tu sketch ignora Analog = 0, así que usamos 1 para representar mínimo
        value = 1 if value == 0 else value
        return {"Analog": value}, "servo", f"Comando servo detectado: {value}%."

    # fallback
    return {"Act1": text.upper()}, "digital", "Texto enviado como comando digital bruto."

def set_command(value):
    st.session_state.command_input = value

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Configuración MQTT")

    broker = st.text_input("Broker", value=DEFAULT_BROKER)
    port = st.number_input("Puerto", min_value=1, max_value=65535, value=DEFAULT_PORT, step=1)
    topic_digital = st.text_input("Topic digital", value=DEFAULT_TOPIC_DIGITAL)
    topic_servo = st.text_input("Topic servo", value=DEFAULT_TOPIC_SERVO)

    st.divider()

    st.markdown("## 🧭 Guía de comandos")
    st.markdown("""
<div class="hint-card"><strong>LED / salida digital</strong><br>ON · OFF · encender · apagar</div>
<div class="hint-card"><strong>Servo</strong><br>25 · 50 · 80 · abrir · cerrar · centro</div>
<div class="hint-card"><strong>Formato JSON</strong><br><code>{"Act1":"ON"}</code> · <code>{"Analog":80}</code></div>
""", unsafe_allow_html=True)

    st.divider()

    st.markdown("## 🎨 Stack visual")
    st.markdown("""
<span class="chip python">Python</span>
<span class="chip mqtt">MQTT</span>
<span class="chip json">JSON</span>
<span class="chip cpp">C++</span>
<span class="chip esp32">ESP32</span>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🎙️ Syntax Voice Control</div>
    <div class="hero-subtitle">
        Interfaz multimodal para enviar comandos de voz y texto a un dispositivo ESP32 mediante MQTT.
    </div>
    <div class="hero-note">
        Inspirada en entornos de programación: colores tipo sintaxis, bloques tipo consola y flujo directo entre voz, JSON y hardware.
    </div>
    <div style="margin-top:14px;">
        <span class="chip python">Python UI</span>
        <span class="chip mqtt">MQTT Broker</span>
        <span class="chip json">JSON Payload</span>
        <span class="chip cpp">Firmware C++</span>
        <span class="chip esp32">ESP32 + Servo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FILA SUPERIOR
# =========================================================
col_hero_1, col_hero_2 = st.columns([1.15, 0.85], gap="large")

with col_hero_1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼️ Contexto visual del proyecto</div>', unsafe_allow_html=True)

    if os.path.exists("voice_ctrl.jpg"):
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_container_width=True)
    else:
        st.markdown("""
        <div class="placeholder-visual">
            Interfaz de control por voz<br>
            Python · MQTT · JSON · ESP32
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col_hero_2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📡 Estado de la conexión lógica</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Broker", broker)
    m2.metric("Puerto", int(port))
    m3.metric("Topics", "2")

    st.markdown('<div class="mini-title">Compatibilidad prevista</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="status-info">
La app queda preparada para enviar comandos digitales y de servo con el mismo formato JSON que usa tu proyecto.
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RECONOCIMIENTO DE VOZ
# =========================================================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎤 Captura de voz</div>', unsafe_allow_html=True)
st.write("Presiona el botón, dicta el comando y luego revisa la transcripción antes de enviarla.")

stt_button = Button(label="🎙️ Activar micrófono", width=260)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "es-ES";

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            value += e.results[i][0].transcript;
        }
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };
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
    recognized = result.get("GET_TEXT").strip()
    st.session_state.recognized_text = recognized
    st.session_state.command_input = recognized

if st.session_state.recognized_text:
    st.markdown('<div class="mini-title">Texto reconocido</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="code-box">{st.session_state.recognized_text}</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ZONA PRINCIPAL DE COMANDOS
# =========================================================
col_main, col_side = st.columns([1.5, 1], gap="large")

with col_main:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⌨️ Editor de comando</div>', unsafe_allow_html=True)

    st.text_input(
        "Comando final",
        key="command_input",
        placeholder="Ej: ON, OFF, 75, abrir, cerrar, centro"
    )

    payload_preview, detected_mode, detected_message = interpret_command(st.session_state.command_input) if st.session_state.command_input.strip() else ({}, "—", "Escribe o dicta un comando para generar el payload.")

    st.markdown('<div class="mini-title">JSON preparado</div>', unsafe_allow_html=True)
    st.code(
        json.dumps(payload_preview, ensure_ascii=False, indent=2) if payload_preview else "{}",
        language="json"
    )

    if st.session_state.command_input.strip():
        if detected_mode == "servo":
            topic_selected = topic_servo
        else:
            topic_selected = topic_digital

        st.markdown(
            f"""
            <div class="status-info">
                <strong>Interpretación:</strong> {detected_message}<br>
                <strong>Topic de destino:</strong> {topic_selected}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🚀 Enviar comando por MQTT"):
            ok, msg = publish_payload(broker, int(port), topic_selected, payload_preview)
            st.session_state.last_payload = payload_preview
            st.session_state.last_topic = topic_selected
            st.session_state.publish_status = msg

            if ok:
                st.markdown(
                    f'<div class="status-ok"><strong>Éxito:</strong> {msg}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="status-warn"><strong>Atención:</strong> {msg}</div>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            '<div class="status-warn"><strong>Atención:</strong> Aún no hay un comando listo para publicar.</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Acciones rápidas</div>', unsafe_allow_html=True)

    qa1, qa2 = st.columns(2)
    if qa1.button("💡 ON"):
        set_command("ON")
        st.rerun()
    if qa2.button("🌑 OFF"):
        set_command("OFF")
        st.rerun()

    qb1, qb2, qb3 = st.columns(3)
    if qb1.button("0%"):
        set_command("1")
        st.rerun()
    if qb2.button("50%"):
        set_command("50")
        st.rerun()
    if qb3.button("100%"):
        set_command("100")
        st.rerun()

    if st.button("↔️ Centro"):
        set_command("centro")
        st.rerun()

    if st.button("🔓 Abrir servo"):
        set_command("abrir")
        st.rerun()

    if st.button("🔒 Cerrar servo"):
        set_command("cerrar")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧾 Último envío</div>', unsafe_allow_html=True)

    if st.session_state.last_payload:
        st.markdown(f"**Topic:** `{st.session_state.last_topic}`")
        st.code(json.dumps(st.session_state.last_payload, indent=2, ensure_ascii=False), language="json")
        if st.session_state.publish_status:
            st.caption(st.session_state.publish_status)
    else:
        st.caption("Todavía no se ha enviado ningún comando.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PIE / AYUDA
# =========================================================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🧠 Sugerencias de uso</div>', unsafe_allow_html=True)

help_cols = st.columns(3)
with help_cols[0]:
    st.markdown("""
<div class="hint-card">
<strong>Comandos de voz sugeridos</strong><br>
“encender” · “apagar” · “servo 80” · “abrir” · “centro”
</div>
""", unsafe_allow_html=True)

with help_cols[1]:
    st.markdown("""
<div class="hint-card">
<strong>Si no responde el hardware</strong><br>
Verifica broker, puerto, topics y que el simulador esté activo.
</div>
""", unsafe_allow_html=True)

with help_cols[2]:
    st.markdown("""
<div class="hint-card">
<strong>Nota para el servo</strong><br>
El valor mínimo práctico se envía como 1 para evitar que el sketch ignore el movimiento.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
