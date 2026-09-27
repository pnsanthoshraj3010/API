import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import librosa
import numpy as np
import sounddevice as sd
import time

# =========================
# 🔑 Gemini API Setup
# =========================
genai.configure(api_key="AIzaSyDMftqElzeXAoRgNKpDUv9kxHW5L_XbWKc")
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# 🔊 Text-to-Speech
# =========================
engine = pyttsx3.init()

def speak(text):
    print("Robot:", text)
    engine.say(text)
    engine.runAndWait()

# =========================
# 🎤 Speech Recognition
# =========================
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

# =========================
# 🎧 RECORD RAW AUDIO (for tone)
# =========================
def record_audio(duration=4, fs=22050):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten(), fs

# =========================
# 🎵 VOICE EMOTION (tone-based)
# =========================
def detect_voice_emotion(audio, fs):
    audio = audio / np.max(np.abs(audio))  # normalize

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

# =========================
# 🧠 TEXT EMOTION (Gemini)
# =========================
def detect_text_emotion(text):
    prompt = f"""
    You are an emotion detection AI.

    Classify the emotion of the sentence STRICTLY into ONE of:
    happy, sad, angry, neutral, excited, scared

    Rules:
    - Do NOT explain
    - Do NOT add punctuation
    - Return ONLY one word
    - Be confident (avoid neutral unless truly neutral)

    Sentence: "{text}"
    """

    try:
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower()

        valid = ["happy", "sad", "angry", "neutral", "excited", "scared"]
        if emotion not in valid:
            return "neutral"

        return emotion
    except:
        return "neutral"

# =========================
# 🔀 COMBINE BOTH EMOTIONS
# =========================
def final_emotion(text_emotion, voice_emotion):
    if text_emotion != "neutral":
        return text_emotion
    return voice_emotion

# =========================
# 🤖 RESPONSE
# =========================
def robot_response(emotion):
    responses = {
        "happy": "That's great to hear!",
        "sad": "I'm here for you.",
        "angry": "Take a breath. I'm with you.",
        "excited": "Wow! That's exciting!",
        "scared": "Don't worry, you're safe.",
        "neutral": "Tell me more."
    }
    return responses.get(emotion, "I understand.")

# =========================
# 👀 EYES
# =========================
def display_eyes(emotion):
    eyes = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "excited": "🤩",
        "scared": "😨",
        "neutral": "😐"
    }
    print(eyes.get(emotion, "😐"), "Eyes")

# =========================
# ⚙️ MOTORS
# =========================
def motor_action(emotion):
    actions = {
        "happy": "Move forward",
        "excited": "Fast movement",
        "sad": "Slow movement",
        "angry": "Stop",
        "scared": "Move backward",
        "neutral": "Idle"
    }
    print("Motors:", actions.get(emotion, "Idle"))

# =========================
# 🔁 MAIN LOOP
# =========================
while True:
    user_input = listen()

    if user_input is None:
        speak("I didn't catch that.")
        continue

    # 🎤 record tone
    audio, fs = record_audio()

    text_emotion = detect_text_emotion(user_input)
    voice_emotion = detect_voice_emotion(audio, fs)

    emotion = final_emotion(text_emotion, voice_emotion)

    print("Text Emotion:", text_emotion)
    print("Voice Emotion:", voice_emotion)
    print("Final Emotion:", emotion)

    display_eyes(emotion)
    motor_action(emotion)

    speak(robot_response(emotion))

    time.sleep(1)