# ==========================================
# 🔊 ULTRASONIC SENSOR - RASPBERRY PI 3 B+
# Equivalent to the Arduino HC-SR04 code
# GPIO 17 = TRIG | GPIO 27 = ECHO
# ==========================================

import RPi.GPIO as GPIO
import time

# ==========================================
# 📌 PIN SETUP (BCM numbering)
# ==========================================
TRIG = 17   # GPIO 17 → Pin 11
ECHO = 27   # GPIO 27 → Pin 13

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# ==========================================
# 📏 MEASURE DISTANCE FUNCTION
# Mirrors Arduino pulseIn() logic exactly
# ==========================================
def measure_distance():
    # --- TRIG pulse (same as Arduino) ---
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.000005)        # delayMicroseconds(5)

    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)         # delayMicroseconds(10)

    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.000005)        # delayMicroseconds(5)

    # --- ECHO: measure pulse width (mirrors pulseIn(4, HIGH)) ---
    # Wait for ECHO to go HIGH
    pulse_start = time.time()
    timeout_start = time.time()

    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()
        if time.time() - timeout_start > 0.04:   # 40ms timeout
            print("Timeout: No echo received")
            return -1

    # Wait for ECHO to go LOW
    pulse_end = time.time()
    timeout_start = time.time()

    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()
        if time.time() - timeout_start > 0.04:   # 40ms timeout
            print("Timeout: Echo stuck HIGH")
            return -1

    # --- DISTANCE CALCULATION (same formula as Arduino) ---
    # Arduino: float Distance = (Time * 0.0343) / 2
    # Time here is in seconds, so convert to microseconds first
    pulse_duration_us = (pulse_end - pulse_start) * 1_000_000  # seconds → microseconds
    distance = (pulse_duration_us * 0.0343) / 2                 # cm

    return round(distance, 2)

# ==========================================
# 🔁 MAIN LOOP (mirrors Arduino loop())
# ==========================================
print("Ultrasonic sensor ready. Measuring...\n")

try:
    while True:
        distance = measure_distance()

        if distance != -1:
            print(f"Distance: {distance} cm")
        else:
            print("Distance: Error")

        time.sleep(1)   # delay(1000) in Arduino

# ==========================================
# 🧹 CLEANUP ON EXIT (Ctrl+C)
# ==========================================
except KeyboardInterrupt:
    print("\nStopped by user.")
    GPIO.cleanup()