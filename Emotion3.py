# ==========================================
# 🤖 VOICE + AI + EMOTION ROBOT (IMPROVED)
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
GEMINI_API_KEY = "AIzaSyDAL8HFAnydYEqvGtqoYBeYfl87kTuN2r4"
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
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
            text = recognizer.recognize_google(audio, language="en-IN")
            print("You:", text)
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print("Listen error:", e)
            return None

# ==========================================
# 🎧 RECORD AUDIO FOR TONE ANALYSIS
# ==========================================
def record_audio(duration=3, fs=22050):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten(), fs

# ==========================================
# 🎵 IMPROVED VOICE EMOTION DETECTION
# Detects: excited, angry, sad, fearful, neutral
# Based on: energy, pitch mean, pitch variance,
#           speech rate, zero-crossing rate
# ==========================================
def detect_voice_emotion(audio, fs):
    # Normalize
    max_amp = np.max(np.abs(audio))
    if max_amp == 0:
        return "neutral", {}

    audio = audio / max_amp

    # --- Feature 1: RMS Energy ---
    rms_energy = np.sqrt(np.mean(audio ** 2))

    # --- Feature 2: Pitch (fundamental frequency) ---
    pitches, magnitudes = librosa.piptrack(y=audio, sr=fs, fmin=75, fmax=600)
    voiced_pitches = pitches[magnitudes > np.percentile(magnitudes, 75)]
    pitch_mean = np.mean(voiced_pitches) if len(voiced_pitches) > 0 else 0
    pitch_std  = np.std(voiced_pitches)  if len(voiced_pitches) > 0 else 0

    # --- Feature 3: Zero-Crossing Rate (speech rate proxy) ---
    zcr = np.mean(librosa.feature.zero_crossing_rate(audio))

    # --- Feature 4: MFCCs (timbre/tension) ---
    mfccs = librosa.feature.mfcc(y=audio, sr=fs, n_mfcc=13)
    mfcc1_mean = np.mean(mfccs[1])   # brightness
    mfcc2_mean = np.mean(mfccs[2])   # tension

    features = {
        "energy":     round(float(rms_energy), 4),
        "pitch_mean": round(float(pitch_mean), 1),
        "pitch_std":  round(float(pitch_std), 1),
        "zcr":        round(float(zcr), 4),
        "mfcc1":      round(float(mfcc1_mean), 2),
        "mfcc2":      round(float(mfcc2_mean), 2),
    }

    print("Voice features:", features)

    # ---- Emotion Rules (priority order) ----
    # EXCITED: high energy + high pitch + high variance + fast rate
    if rms_energy > 0.06 and pitch_mean > 200 and pitch_std > 40 and zcr > 0.08:
        return "excited", features

    # ANGRY: high energy + low-mid pitch + low variance (flat, forceful)
    if rms_energy > 0.05 and 110 < pitch_mean < 190 and pitch_std < 35 and mfcc2_mean < -2:
        return "angry", features

    # FEARFUL / SCARED: medium-high energy + very high pitch + high variance
    if rms_energy > 0.03 and pitch_mean > 230 and pitch_std > 55:
        return "scared", features

    # SAD: low energy + low pitch + slow rate
    if rms_energy < 0.02 and pitch_mean < 140 and zcr < 0.05:
        return "sad", features

    # HAPPY: moderate-high energy + moderate pitch + bright MFCC
    if rms_energy > 0.04 and 150 < pitch_mean < 230 and mfcc1_mean > 5:
        return "happy", features

    return "neutral", features

# ==========================================
# 🧠 TEXT EMOTION DETECTION (Gemini)
# ==========================================
def detect_text_emotion(text):
    prompt = f"""Analyze the emotional tone of this sentence and return EXACTLY ONE word from this list:
happy, sad, angry, neutral, excited, scared

Rules:
- Return only the single emotion word, nothing else
- No punctuation, no explanation
- Choose the most dominant emotion

Sentence: "{text}"
Emotion:"""

    try:
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower().split()[0]
        valid = ["happy", "sad", "angry", "neutral", "excited", "scared"]
        return emotion if emotion in valid else "neutral"
    except:
        return "neutral"

# ==========================================
# 🔀 IMPROVED EMOTION FUSION
# Weighs both sources; voice tone is stronger
# for high-energy states, text for cognitive ones
# ==========================================
EMOTION_INTENSITY = {
    "excited": 3,
    "angry":   3,
    "scared":  2,
    "happy":   2,
    "sad":     1,
    "neutral": 0,
}

def final_emotion(text_emotion, voice_emotion, voice_features):
    # If both agree → confident result
    if text_emotion == voice_emotion:
        return text_emotion

    # If one is neutral → use the other
    if text_emotion == "neutral":
        return voice_emotion
    if voice_emotion == "neutral":
        return text_emotion

    # Both disagree and neither is neutral:
    # High energy voice → trust voice (physical state is dominant)
    energy = voice_features.get("energy", 0)
    if energy > 0.05:
        return voice_emotion

    # Low energy → trust text (cognitive/semantic state)
    return text_emotion

# ==========================================
# 🤖 CHAT AI WITH EMOTION-AWARE PROMPTING
# ==========================================
def ask_ai(text, emotion):
    tone_hints = {
        "happy":   "The user sounds happy. Respond warmly and match their positive energy.",
        "excited": "The user sounds excited. Be enthusiastic and energetic in your reply.",
        "sad":     "The user sounds sad. Be gentle, empathetic, and supportive.",
        "angry":   "The user sounds angry or frustrated. Stay calm, be understanding, do not escalate.",
        "scared":  "The user sounds scared or anxious. Be reassuring and calm.",
        "neutral": "Respond helpfully and naturally.", 
    }
    tone_instruction = tone_hints.get(emotion, tone_hints["neutral"])

    prompt = f"""{tone_instruction}

User said: "{text}"

Reply in 1-2 short sentences, naturally. No asterisks or markdown."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "I didn't understand that."
    except Exception as e:
        print("API Error:", e)
        return "I'm having a little trouble right now."

# ==========================================
# ⚙️ MOTOR COMMANDS
# ==========================================
def forward():  speak("Moving forward")
def backward(): speak("Moving backward")
def left():     speak("Turning left")
def right():    speak("Turning right")
def stop():     speak("Stopping")

# ==========================================
# 👀 DISPLAY EYES
# ==========================================
EMOTION_EYES = {
    "happy":   "😊",
    "sad":     "😢",
    "angry":   "😠",
    "excited": "🤩",
    "scared":  "😨",
    "neutral": "😐",
}

def display_eyes(emotion):
    eye = EMOTION_EYES.get(emotion, "😐")
    print(f"\n  Eyes: {eye}  [{emotion.upper()}]\n")

# ==========================================
# 🚗 MOTOR BEHAVIOR FROM EMOTION
# ==========================================
def motor_action(emotion):
    actions = {
        "happy":   (forward,  "Happy — moving forward!"),
        "excited": (forward,  "Excited — full speed!"),
        "sad":     (None,     "Sad — slow movement..."),
        "angry":   (stop,     "Angry — stopping."),
        "scared":  (backward, "Scared — backing away!"),
        "neutral": (None,     "Neutral — idling."),
    }
    action_fn, message = actions.get(emotion, (None, "Idling."))
    print("Motor:", message)
    if action_fn:
        action_fn()
    else:
        speak(message)

# ==========================================
# 🧠 PROCESS INPUT
# ==========================================
COMMANDS = {
    "forward": forward,
    "back":    backward,
    "left":    left,
    "right":   right,
    "stop":    stop,
}

def process(text, audio, fs):
    # --- Command mode (direct motor control) ---
    for keyword, fn in COMMANDS.items():
        if keyword in text:
            fn()
            return

    # --- Emotion detection (both channels) ---
    text_emotion               = detect_text_emotion(text)
    voice_emotion, voice_feats = detect_voice_emotion(audio, fs)
    emotion                    = final_emotion(text_emotion, voice_emotion, voice_feats)

    print(f"  Text emotion : {text_emotion}")
    print(f"  Voice emotion: {voice_emotion}")
    print(f"  Final emotion: {emotion}")

    display_eyes(emotion)
    motor_action(emotion)

    # --- Emotion-aware AI reply ---
    reply = ask_ai(text, emotion)
    speak(reply)

# ==========================================
# 🔁 MAIN LOOP
# ==========================================
speak("System ready. I'm listening.")

while True:
    # Record audio FIRST (captures the actual voice tone)
    audio, fs = record_audio(duration=4)

    # Then transcribe from the same recording
    try:
        import io
        import scipy.io.wavfile as wav
        buf = io.BytesIO()
        wav.write(buf, fs, (audio * 32767).astype(np.int16))
        buf.seek(0)

        with sr.AudioFile(buf) as source:
            raw_audio = recognizer.record(source)
        text = recognizer.recognize_google(raw_audio, language="en-IN").lower()
        print("You:", text)
        process(text, audio, fs)

    except sr.UnknownValueError:
        speak("I didn't catch that, could you repeat?")
    except Exception as e:
        print("Error:", e)
        speak("Something went wrong.")

    time.sleep(0.5)