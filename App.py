import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3
import re
import time

# LM Studio API details
API_URL = """add your API URL here""""
MODEL_NAME = """your model name here"""

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 1)

def remove_emojis(text):
    return re.sub(r'[^\w\s,.!?]', '', text)

def text_to_speech(text):
    """Converts text to speech using a globally initialized TTS engine."""
    clean_text = remove_emojis(text)
    tts_engine.say(clean_text)
    tts_engine.runAndWait()

def speech_to_text():
    """Converts voice input to text with extended listening time and error handling."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Please speak now!")
        try:
            # Extended listening time for better recognition
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio. Please try again."
        except sr.RequestError:
            return "Could not request results from the speech recognition service."
        except Exception as e:
            return f"Error: {e}"
    return ""

# Streamlit UI
st.set_page_config(page_title="Mental Health Chatbot", layout="wide")
st.title("🧠 Mental Health Support Chatbot")
st.write("This chatbot provides mental health support. Please note: It is not a substitute for professional help.")

# Initialize chat history if not available
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I support you today?"}]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

col_input, col_icons = st.columns([10, 2])
with col_input:
    user_input = st.chat_input("Type your message here...")

with col_icons:
    icon_col1, icon_col2, icon_col3 = st.columns([1, 1, 1])
    # Text input mode icon
    if icon_col1.button("🅰️"):
        st.info("Text input mode active. Please type your message.")
    # Voice input mode icon
    if icon_col2.button("🎤"):
        user_input = speech_to_text()
        st.write(f"🗣️ You said: **{user_input}**")
    # Reset chat button icon
    if icon_col3.button("🔄"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I support you today?"}]
        st.rerun()

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("💬 Thinking..."):
        time.sleep(1)
        payload = {
            "model": MODEL_NAME,
            "messages": st.session_state.messages,
            "temperature": 0.7
        }
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            response_json = response.json()
            bot_reply = response_json.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't process that.")
        except requests.exceptions.Timeout:
            bot_reply = "⏳ The server is taking too long to respond. Please try again later."
        except requests.exceptions.RequestException as e:
            bot_reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    text_to_speech(bot_reply)