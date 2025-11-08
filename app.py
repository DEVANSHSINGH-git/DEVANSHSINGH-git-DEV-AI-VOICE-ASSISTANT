import streamlit as st
import pyttsx3
import speech_recognition as sr
import pandas as pd
import random
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import pywhatkit
import webbrowser
import wikipedia
import requests
import pyjokes
import threading

# ----------------- Initialize -----------------
# ================== Streamlit UI Setup ==================
st.set_page_config(page_title="DEV - AI Voice Assistant", layout="wide")

# Apply custom CSS for a futuristic assistant look
st.markdown("""
    <style>
    /* Background gradient */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 10% 20%, #0f2027, #203a43, #2c5364);
        color: #f8f8f8;
        font-family: 'Poppins', sans-serif;
    }

    /* Title glow */
    h1 {
        text-align: center;
        color: #00e0ff;
        font-size: 45px;
        text-shadow: 0px 0px 20px #00e0ff;
        margin-bottom: -10px;
    }

    /* Subtitle */
    h3 {
        text-align: center;
        color: #00b4d8;
        font-weight: 400;
        margin-bottom: 20px;
        font-size: 20px;
    }

    /* Horizontal line */
    hr {
        border: 1px solid #00e0ff;
        width: 80%;
        margin: auto;
        opacity: 0.4;
    }

    /* Input elements */
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.08);
        color: #f8f8f8;
        border-radius: 10px;
        border: 1px solid #00e0ff;
        font-size: 16px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00e0ff, #00b4d8);
        color: black;
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0px 0px 10px #00e0ff;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #00b4d8, #0096c7);
        transform: scale(1.05);
        box-shadow: 0px 0px 20px #00e0ff;
    }

    /* Response area */
    .stTextArea textarea {
        background-color: rgba(255,255,255,0.08);
        color: #00e0ff;
        border: 1px solid #00e0ff;
        border-radius: 10px;
        font-size: 16px;
    }

    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ================== Page Header ==================
st.markdown("<h1>🧠 DEV – AI Voice Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h3>Welcome back, Devansh. I am online and ready to assist you.</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

engine = pyttsx3.init()

def speak(text):
    """Speak text asynchronously to prevent Streamlit runtime errors."""
    def run_speech():
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            # Safely ignore 'run loop already started' during Streamlit reruns
            pass

    # Run pyttsx3 in a separate background thread
    threading.Thread(target=run_speech, daemon=True).start()
# Load intents dataset
# Use raw string for Windows paths
data = pd.read_csv(r'C:\Users\Devanshhh\Desktop\DEV_AI_MODEL\model_intents.csv')

import torch  # add this at the top if not already imported

# Force model to load on CPU to avoid meta tensor error
device = torch.device("cpu")
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Compute embeddings after loading model
data['embeddings'] = data['patterns'].apply(lambda x: model.encode(x))


# WhatsApp contacts
contacts = {
    "mom": "+91993099795",
    "dad": "+919920578951",
    "devansh": "+919930993699",
    "siddharth": "+918010340539",
    "appu": "+918828216775",
    "shubham": "+918369246841",
    "dweep": "+917710978922",
    "ria": "+919082432506",
    "srishti": "+919820125493",
    "shiv": "+918530496292",
    "aneesh": "+918767688040",
    "ayush": "+918104722563",
    "kk": "+919702479662",
    "nitin": "+919022589784",
    "mama": "+919324024818"
}

# ----------------- NLP Prediction -----------------
def predict_intent(user_input):
    input_emb = model.encode(user_input)
    similarities = data['embeddings'].apply(lambda x: cosine_similarity([input_emb], [x])[0][0])
    idx = similarities.idxmax()
    return data.loc[idx, 'intent'], data.loc[idx, 'response']

# ----------------- Weather Function -----------------
def get_weather(city):
    api_key = "1a0b53c75d3d5444eaa2c945b1cd0b6e"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url)
    info = res.json()
    if info.get("cod") != "404":
        temp = info['main']['temp']
        desc = info['weather'][0]['description']
        return f"Current temperature in {city} is {temp}°C with {desc}."
    else:
        return "City not found."

# ----------------- Handle Intents -----------------
def handle_intent(intent, query):
    if intent == "greeting":
        response = random.choice(data[data['intent']=="greeting"]['response'].tolist())
    elif intent == "time_query":
        response = datetime.datetime.now().strftime("The time is %H:%M")
    elif intent == "date_query":
        response = datetime.datetime.now().strftime("Today's date is %d %B %Y")
    elif intent == "joke":
        response = pyjokes.get_joke()
    elif intent == "weather":
        response = get_weather(query.replace("weather","").strip())
    elif intent == "wikipedia":
        try:
            result = wikipedia.summary(query.replace("wikipedia",""), sentences=2)
            response = f"According to Wikipedia: {result}"
        except:
            response = "Sorry, I couldn't find that on Wikipedia."
    elif intent == "youtube":
        webbrowser.open("https://www.youtube.com")
        response = "Opening YouTube..."
    elif intent == "google":
        webbrowser.open(f"https://www.google.com/search?q={query}")
        response = "Here are the search results..."
    elif intent == "send_whatsapp":
        try:
            words = query.split()
            name = words[-1]
            if name in contacts:
                msg = st.text_input("Enter message for " + name)
                pywhatkit.sendwhatmsg_instantly(contacts[name], msg)
                response = f"WhatsApp message sent to {name}."
            else:
                response = "Contact not found."
        except:
            response = "Error sending WhatsApp message."
    elif intent == "goodbye":
        response = random.choice(data[data['intent']=="goodbye"]['response'].tolist())
    else:
        response = random.choice(data[data['intent']=="fallback"]['response'].tolist())
    return response

# ----------------- Streamlit Input -----------------
mode = st.radio("Choose input mode:", ["Text", "Speech"])

if mode == "Text":
    user_input = st.text_input("You:")
    if st.button("Send") and user_input:
        intent, _ = predict_intent(user_input)
        response = handle_intent(intent, user_input)
        st.text_area("Assistant:", value=response, height=150)
        speak(response)

elif mode == "Speech":
    if st.button("Speak"):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            user_input = r.recognize_google(audio)
            st.text_area("You said:", value=user_input, height=50)
            intent, _ = predict_intent(user_input)
            response = handle_intent(intent, user_input)
            st.text_area("Assistant:", value=response, height=150)
            speak(response)
        except:
            st.warning("Sorry, could not recognize your voice.")
