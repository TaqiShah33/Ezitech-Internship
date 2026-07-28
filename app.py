import os
import tempfile
import streamlit as st
from groq import Groq
from gtts import gTTS
import speech_recognition as sr

# 1. Page Configuration & Futuristic Cyberpunk Styling
st.set_page_config(page_title="J.A.R.V.I.S. // Holographic HUD", page_icon="🔵", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 40%, #0b192c 0%, #040914 70%, #010408 100%);
        color: #c9d1d9;
        font-family: 'Courier New', Courier, monospace;
    }
    header {visibility: hidden;}
    
    .jarvis-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #30363d;
        padding-bottom: 15px;
        margin-bottom: 15px;
    }
    .jarvis-title {
        font-family: 'Courier New', Courier, monospace;
        color: #00f0ff;
        font-size: 20px;
        font-weight: bold;
        letter-spacing: 3px;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
    }
    .status-badge {
        background-color: rgba(0, 240, 255, 0.1);
        color: #00f0ff;
        border: 1px solid #00f0ff;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 11px;
        letter-spacing: 1px;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
    }

    /* --- HOLOGRAPHIC REACTOR HUD ANIMATION --- */
    .hud-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0 20px 0;
        position: relative;
        height: 160px;
    }
    .reactor-ring {
        position: absolute;
        width: 140px;
        height: 140px;
        border: 2px dashed rgba(0, 240, 255, 0.4);
        border-radius: 50%;
        animation: spin-clockwise 12s linear infinite;
    }
    .reactor-ring-outer {
        position: absolute;
        width: 170px;
        height: 170px;
        border: 2px dotted rgba(0, 240, 255, 0.25);
        border-radius: 50%;
        animation: spin-counter 18s linear infinite;
    }
    .reactor-core {
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.2) 0%, rgba(4, 9, 20, 0.8) 80%);
        border: 2px solid #00f0ff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.5);
        color: #00f0ff;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 0 8px #00f0ff;
    }
    @keyframes spin-clockwise {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes spin-counter {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(-360deg); }
    }

    div[data-testid="stAudioInput"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Header Layout (JARVIS style)
st.markdown("""
    <div class="jarvis-header">
        <div class="jarvis-title">J.A.R.V.I.S. // HUD SYSTEM</div>
        <div><span class="status-badge">ONLINE</span></div>
    </div>
""", unsafe_allow_html=True)

# 3. Holographic Reactor HUD Visual Element
st.markdown("""
    <div class="hud-container">
        <div class="reactor-ring-outer"></div>
        <div class="reactor-ring"></div>
        <div class="reactor-core">J.A.R.V.I.S.</div>
    </div>
""", unsafe_allow_html=True)

# 4. API Setup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# 5. Session State Initialization
if "user_text" not in st.session_state:
    st.session_state.user_text = None
if "ai_reply" not in st.session_state:
    st.session_state.ai_reply = None
if "audio_output_path" not in st.session_state:
    st.session_state.audio_path = None

# 6. Processing Engine
def process_voice_interaction(audio_value):
    recognizer = sr.Recognizer()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_value.getvalue())
        temp_audio_path = temp_audio.name

    try:
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are J.A.R.V.I.S., an advanced, highly intelligent, and ultra-concise AI assistant. Respond with technical precision, polite sophistication, and brief phrasing."},
                {"role": "user", "content": user_text},
            ],
            max_tokens=100,
        )
        ai_reply = response.choices[0].message.content.strip()

        tts = gTTS(text=ai_reply, lang="en", slow=False)
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)

        return user_text, ai_reply, fp.name

    except Exception as e:
        st.error(f"System Error: {e}")
        return None, None, None

# 7. Interface Core & Input Listener
st.markdown("<p style='font-family: monospace; color: #8b949e; text-align: center;'>Awaiting audio input directive...</p>", unsafe_allow_html=True)

audio_value = st.audio_input("")

if audio_value is not None:
    with st.spinner("Processing voice command through neural net..."):
        u_text, a_reply, a_path = process_voice_interaction(audio_value)
        if a_reply and a_path:
            st.session_state.user_text = u_text
            st.session_state.ai_reply = a_reply
            st.session_state.audio_path = a_path

# 8. Persistent Output Rendering with Autoplay Enabled
if st.session_state.ai_reply and st.session_state.audio_path:
    st.markdown(f"""
        <div style='background-color: #161b22; border-left: 4px solid #00f0ff; padding: 12px; border-radius: 6px; margin-bottom: 10px;'>
            <b style='color: #00f0ff;'>Command:</b> {st.session_state.user_text}
        </div>
        <div style='background-color: #161b22; border-left: 4px solid #00ff80; padding: 12px; border-radius: 6px; margin-bottom: 20px;'>
            <b style='color: #00ff80;'>J.A.R.V.I.S.:</b> {st.session_state.ai_reply}
        </div>
    """, unsafe_allow_html=True)
    
    # Enabled automatic playback using Streamlit's built-in autoplay parameter
    st.audio(st.session_state.audio_path, format="audio/mp3", autoplay=True)