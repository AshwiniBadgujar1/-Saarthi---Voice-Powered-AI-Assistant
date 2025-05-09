import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
from datetime import datetime
import os
import random
from dotenv import load_dotenv
import openai

#  CONFIGURATION 
st.set_page_config(
    page_title="Saarthi - AI Assistant",
    layout="centered",
    page_icon="🎙️"
)
st.title("🎙️ Saarthi - AI Assistant")

# Load environment variables
load_dotenv()
USE_OPENAI_API = False  # Set to True if you want to use GPT
openai.api_key = os.getenv("OPENAI_API_KEY") if USE_OPENAI_API else None

#  CONSTANTS 
LANGUAGES = {
    "English": {"code": "en", "icon": "🇬🇧"},
    "Hindi": {"code": "hi", "icon": "🇮🇳"},
    "Marathi": {"code": "mr", "icon": "🇮🇳"}
}

FAREWELL_MESSAGES = {
    "en": "Session ended. Have a nice day!",
    "hi": "सत्र समाप्त हुआ। आपका दिन शुभ हो!",
    "mr": "सत्र समाप्त. तुमचा दिवस छान जावो!"
}

# SESSION STATE 
if "history" not in st.session_state:
    st.session_state.history = []
if "audio_files" not in st.session_state:
    st.session_state.audio_files = []

#  SIDEBAR SETTINGS 
with st.sidebar:
    st.header("Settings ⚙️")
    language_choice = st.selectbox(
        "🌐 Choose Language",
        list(LANGUAGES.keys()),
        format_func=lambda x: f"{LANGUAGES[x]['icon']} {x}"
    )
    selected_lang = LANGUAGES[language_choice]

#  FUNCTIONS 

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now.")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        return recognizer.recognize_google(audio, language=selected_lang["code"])
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio")
    except sr.RequestError as e:
        st.error(f"❌ Speech recognition error: {e}")
    except Exception as e:
        st.error(f"❌ Microphone error: {e}")
    return None

def generate_response(prompt):
    prompt = prompt.lower()
    now = datetime.now()

    responses = {
        "English": {
            "time": f"The current time is {now.strftime('%I:%M %p')}.",
            "name": "I'm Saarthi, your voice assistant.",
            "how": "I'm doing great! How about you?",
            "date": f"Today's date is {now.strftime('%B %d, %Y')}.",
            "joke": random.choice([
                "Why don't programmers like nature? Too many bugs.",
                "Why do devs prefer dark mode? Light attracts bugs!"
            ]),
            "default": "Sorry, I didn't understand that. Could you rephrase?"
        },
        "Hindi": {
            "time": f"अभी समय है {now.strftime('%I:%M %p')}।",
            "name": "मेरा नाम सारथी है।",
            "how": "मैं अच्छा हूँ! आप कैसे हैं?",
            "date": f"आज की तारीख है {now.strftime('%d %B %Y')}।",
            "joke": "डिवेलपर ने मजाक क्यों छोड़ा? क्योंकि वह बग्स से थक गया था!",
            "default": "मुझे खेद है, मैं यह नहीं समझ पाया। कृपया फिर से कहें।"
        },
        "Marathi": {
            "time": f"सध्या वेळ आहे {now.strftime('%I:%M %p')}.",
            "name": "माझं नाव सारथी आहे.",
            "how": "मी मजेत आहे! तुम्ही कसे आहात?",
            "date": f"आजची तारीख आहे {now.strftime('%d %B %Y')}.",
            "joke": "प्रोग्रॅमरने नोकरी का सोडली? कारण त्याने सर्व कॅश वापरून टाकला!",
            "default": "माझ्या माफीसह, मी ते समजू शकलो नाही. कृपया पुन्हा प्रयत्न करा."
        }
    }

    lang_responses = responses[language_choice]
    if any(word in prompt for word in ["time", "वेळ", "समय"]):
        return lang_responses["time"]
    elif any(phrase in prompt for phrase in ["your name", "तुमचं नाव", "तुम्हारा नाम"]):
        return lang_responses["name"]
    elif any(phrase in prompt for phrase in ["how are you", "कसे आहात", "कैसे हो"]):
        return lang_responses["how"]
    elif any(word in prompt for word in ["date", "तारीख"]):
        return lang_responses["date"]
    elif any(word in prompt for word in ["joke", "विनोद", "मजेदार"]):
        return lang_responses["joke"]
    return lang_responses["default"]

def speak(text):
    try:
        # Clean up old audio files
        for file in st.session_state.audio_files:
            try:
                if os.path.exists(file):
                    os.unlink(file)
            except:
                pass
        st.session_state.audio_files = []

        # Generate new audio
        tts = gTTS(text=text, lang=selected_lang["code"])
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        st.session_state.audio_files.append(fp.name)

        # Play audio
        audio_bytes = open(fp.name, "rb").read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"🔇 Audio error: {str(e)}")

#  MAIN INTERFACE 


col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🎤 Speak", use_container_width=True):
        user_input = recognize_speech()
        if user_input:
            st.session_state.history.append(("user", user_input))
            response = generate_response(user_input)
            st.session_state.history.append(("assistant", response))
            speak(response)

with col2:
    text_input = st.text_input("Type your message here:", label_visibility="collapsed")
    if text_input:
        st.session_state.history.append(("user", text_input))
        response = generate_response(text_input)
        st.session_state.history.append(("assistant", response))
        speak(response)

# Chat History
for role, msg in st.session_state.history:
    st.chat_message(role).write(msg)

# Close Chat
if st.button("❌ Close Chat", use_container_width=True):
    farewell_msg = FAREWELL_MESSAGES.get(selected_lang["code"], FAREWELL_MESSAGES["en"])
    st.success(farewell_msg)
    speak(farewell_msg)
    st.stop()
