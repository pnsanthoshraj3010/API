# ==========================================
# 🤖 VOICE + AI + EMOTION ROBOT (COMBINED)
# ==========================================

import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import librosa
import numpy as np
import sounddevice as sd
import time

# ==========================================
# 🔑 GEMINI SETUP
# ==========================================
GEMINI_API_KEY = "AIzaSyAibibSJhCwu9rufV1oJtz9IbnOUqBinmQ"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================================
# 🔊 TEXT TO SPEECH
# ==========================================
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()

# ==========================================
# 🎤 SPEECH RECOGNITION
# ==========================================
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="en-IN")
            print("You:", text)
            return text.lower()
        except:
            return None

# ==========================================
# 🎧 RECORD AUDIO FOR TONE
# ==========================================
def record_audio(duration=3, fs=22050):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten(), fs

# ==========================================
# 🎵 VOICE EMOTION
# ==========================================
def detect_voice_emotion(audio, fs):
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) != 0 else audio

    energy = np.mean(audio**2)

    pitches, _ = librosa.piptrack(y=audio, sr=fs)
    pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0

    if energy > 0.03 and pitch > 180:
        return "excited"
    elif energy > 0.025 and pitch < 140:
        return "angry"
    elif energy < 0.015:
        return "sad"
    else:
        return "neutral"

# ==========================================
# 🧠 TEXT EMOTION (AI)
# ==========================================
def detect_text_emotion(text):
    prompt = f"""
    Classify emotion into ONE word:
    happy, sad, angry, neutral, excited, scared

    Sentence: "{text}"
    """

    try:
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower()

        valid = ["happy", "sad", "angry", "neutral", "excited", "scared"]
        return emotion if emotion in valid else "neutral"
    except:
        return "neutral"

# ==========================================
# 🔀 FINAL EMOTION
# ==========================================
def final_emotion(text_emotion, voice_emotion):
    return text_emotion if text_emotion != "neutral" else voice_emotion

# ==========================================
# 🤖 CHAT AI
# ==========================================
def ask_ai(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "I didn't understand"
    except Exception as e:
        print("API Error:", e)
        return "error"

# ==========================================
# ⚙️ MOTOR COMMANDS
# ==========================================
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

# ==========================================
# 👀 DISPLAY
# ==========================================
def display_eyes(emotion):
    eyes = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "excited": "🤩",
        "scared": "😨",
        "neutral": "😐"
    }
    print("Eyes:", eyes.get(emotion, "😐"))

# ==========================================
# 🚗 MOTOR BEHAVIOR BASED ON EMOTION
# ==========================================
def motor_action(emotion):
    actions = {
        "happy": forward,
        "excited": forward,
        "sad": lambda: print("Motors: Slow movement"),
        "angry": stop,
        "scared": backward,
        "neutral": lambda: print("Motors: Idle")
    }

    action = actions.get(emotion)
    if callable(action):
        action()

# ==========================================
# 🧠 PROCESS INPUT
# ==========================================
def process(text):

    # 🔹 COMMAND MODE
    if "forward" in text:
        forward()
        return
    elif "back" in text:
        backward()
        return
    elif "left" in text:
        left()
        return
    elif "right" in text:
        right()
        return
    elif "stop" in text:
        stop()
        return

    # 🔹 EMOTION DETECTION
    audio, fs = record_audio()

    text_emotion = detect_text_emotion(text)
    voice_emotion = detect_voice_emotion(audio, fs)
    emotion = final_emotion(text_emotion, voice_emotion)

    print("Text Emotion:", text_emotion)
    print("Voice Emotion:", voice_emotion)
    print("Final Emotion:", emotion)

    display_eyes(emotion)
    motor_action(emotion)

    # 🔹 AI RESPONSE
    reply = ask_ai(text)
    speak(reply)

# ==========================================
# 🔁 MAIN LOOP
# ==========================================
speak("System Ready")

while True:
    voice = listen()

    if voice:
        process(voice)
    else:
        speak("I didn't catch that")

    time.sleep(1)