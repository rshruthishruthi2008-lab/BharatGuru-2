import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import os

API_KEY = st.secrets.get("AQ.Ab8RN6LWqdI7WcJBEyAiGKh7lOLhpE2Xq1fuAU_c8Y5nOzNEFQ")

st.set_page_config(page_title="Bharat Guru.2 V4", page_icon="🇮🇳")
st.title("🇮🇳 Bharat Guru.2 V4 - Voice Guru")

with st.sidebar:
    exam = st.selectbox("Exam / Class", ["KPSC","UPSC","Class 12","Class 10","NDA","Railway"], index=2)
    lang = st.selectbox("Language", ["Kannada","English","Hindi","Tamil","Telugu","Malayalam"], index=2)
    subject = st.selectbox("Subject", ["Maths","Science","Polity","History","All"], index=0)
    voice_on = st.toggle("🔊 Voice Answer ON", value=True)
    st.success(f"Ready: {exam} | {lang}")

client = genai.Client(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages=[]

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

# VOICE INPUT
audio = st.audio_input("🎙️ Ask by Voice")
text_from_voice = None
if audio:
    with st.spinner("Sun raha hoon..."):
        r = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=["Transcribe audio", types.Part.from_bytes(data=audio.getvalue(), mime_type="audio/wav")]
        )
        text_from_voice = r.text
        st.info(f"🎤 You said: {text_from_voice}")

q = st.chat_input(f"Ask about {subject}...")
final_q = text_from_voice if text_from_voice else q

if final_q:
    st.session_state.messages.append({"role":"user","content":final_q})
    st.chat_message("user").write(final_q)
    
    with st.chat_message("assistant"):
        ph = st.empty()
        full = ""
        stream = client.models.generate_content_stream(
            model="gemini-3.1-flash-lite", # 2 sec super fast
            contents=f"You are Kalam Sir for {exam} {subject}. Answer in {lang}. Simple for {exam} students. Question: {final_q}"
        )
        for chunk in stream:
            if chunk.text:
                full += chunk.text
                ph.write(full + "▌")
        ph.write(full)
        
        # SPEAK ANSWER
        if voice_on and full:
            try:
                code_map = {"Hindi":"hi","Kannada":"kn","Tamil":"ta","Telugu":"te","Malayalam":"ml","English":"en"}
                lang_code = code_map.get(lang, "hi")
                tts = gTTS(text=full[:400], lang=lang_code) # first 400 chars
                tts.save("ans.mp3")
                st.audio("ans.mp3", autoplay=True)
            except:
                pass

    st.session_state.messages.append({"role":"assistant","content":full})