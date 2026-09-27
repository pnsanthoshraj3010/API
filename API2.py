# ==============================
#   VOICE CONTROLLED CHATBOT ROBOT
# ==============================

import pyttsx3
import speech_recognition as sr
import google.generativeai as genai

# ==============================
# CONFIG
# ==============================

GEMINI_API_KEY = "AIzaSyC0-l4fk9dvazTchCtE1xMatIYuhHztOJM"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# ==============================
# VOICE SETUP
# ==============================

engine = pyttsx3.init()
engine.setProperty('rate', 170)

recognizer = sr.Recognizer()

def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="en-IN")
            print("You:", text)
            return text.lower()
        except:
            return None

# ==============================
# MOTOR COMMANDS (SIMULATION)
# ==============================

def forward():
    speak("Moving forward")

def backward():
    speak("Moving backward")

def left():
    speak("Turning left")

def right():
    speak("Turning right")

def stop():
    speak("Stopping")

# ==============================
# AI FUNCTION
# ==============================

def ask_ai(prompt):
    try:
        response = model.generate_content(prompt)

        if response and response.text:
            return response.text.strip()
        else:
            return "I didn't understand"

    except Exception as e:
        print("API Error:", e)
        return "error"

# ==============================
# COMMAND PROCESSOR
# ==============================

def process(text):

    # COMMAND MODE
    if "forward" in text:
        forward()

    elif "back" in text:
        backward()

    elif "left" in text:
        left()

    elif "right" in text:
        right()

    elif "stop" in text:
        stop()

    # CHATBOT MODE
    else:
        reply = ask_ai(text)
        speak(reply)

# ==============================
# MAIN LOOP
# ==============================

speak("System Ready")

while True:
    voice = listen()

    if voice:
        process(voice)