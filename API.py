# ==============================
#   AI ROBOT (FAKE-RPI VERSION)
# ==============================

# ---- FAKE GPIO SETUP ----
from fake_rpi.RPi import GPIO   # <-- important
import time

import pyttsx3
import speech_recognition as sr
import google.generativeai as genai

# ==============================
#   CONFIG
# ==============================

GEMINI_API_KEY = "AIzaSyBnMSlfoRyjm008qWd0U0pYfT-1IDWn15s"

# Motor Pins (virtual)
IN1, IN2, IN3, IN4 = 17, 18, 27, 22

# Line Sensors (virtual)
LEFT_SENSOR = 23
RIGHT_SENSOR = 24

# ==============================
#   GPIO SETUP
# ==============================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in [IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

GPIO.setup(LEFT_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_SENSOR, GPIO.IN)

# ==============================
#   GEMINI SETUP
# ==============================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ==============================
#   VOICE SYSTEM
# ==============================

engine = pyttsx3.init()
engine.setProperty('rate', 180)

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
#   MOTOR CONTROL (SIMULATED)
# ==============================

def stop():
    print("Motor: STOP")

def forward():
    print("Motor: FORWARD")

def backward():
    print("Motor: BACKWARD")

def left():
    print("Motor: LEFT")

def right():
    print("Motor: RIGHT")

def round_turn():
    print("Motor: ROUND TURN")
    time.sleep(1)

# ==============================
#   LINE FOLLOW (SIMULATION)
# ==============================

def line_follow():
    # Simulated sensor values (change manually for testing)
    left_val = 0
    right_val = 0

    if left_val == 0 and right_val == 0:
        forward()
    elif left_val == 1 and right_val == 0:
        left()
    elif left_val == 0 and right_val == 1:
        right()
    else:
        stop()

# ==============================
#   GEMINI
# ==============================

def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.lower()
    except:
        return "error"

# ==============================
#   COMMAND HANDLER
# ==============================

def handle_command(text):
    global mode

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
    elif "round" in text:
        round_turn()

    elif "auto" in text or "line" in text:
        mode = "auto"
        speak("Auto mode enabled")

    elif "manual" in text:
        mode = "manual"
        speak("Manual mode enabled")

# ==============================
#   MAIN LOOP
# ==============================

mode = "manual"

print("=== AI Robot Started (Simulation Mode) ===")
speak("System Ready")

try:
    while True:

        voice = listen()

        if voice:
            reply = ask_gemini(voice)
            speak(reply)

            handle_command(voice)

        if mode == "auto":
            line_follow()
            time.sleep(0.5)

except KeyboardInterrupt:
    print("Shutting down...")
    GPIO.cleanup()