# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import os
import time
import sys
#Check where the program is running on what platforms (macos,linux,windows,streamlit cloud,etc)
DEMO_MODE = os.environ.get("STREAMLIT_DEMO", "false").lower() == "true"

try:
    if not DEMO_MODE:
        from FocusEye import run_detection  # real YOLO detection
except Exception:
    DEMO_MODE = True

# ---------------- Sound function ----------------
def play_alert():
    if not DEMO_MODE:
        os.system("afplay alertsound.mp3 &")  # MacOS only

# ---------------- Streamlit layout ----------------
st.markdown("<h1 style='text-align:center; color:#00BFFF;'>FocusEye</h1>", unsafe_allow_html=True)

menu = option_menu("Main Menu", ["Home", "About", "Code"], icons=['house', 'info-circle', 'code-slash'], menu_icon="cast")

# ---------------- Home Page ----------------
if menu == "Home":
    st.header("Home Page")
    st.markdown("FocusEye helps you stay focused by detecting your phone and warning you when you get distracted.")

    focus_time = st.number_input("Set focus session (minutes)", min_value=1, max_value=180, value=25)
    start = st.button("Start Focus Session")

    if start:
        st.success(f"Focus session started for {focus_time} minutes!")
        alert = st.empty()

    if DEMO_MODE:
        st.warning("Running in Demo Mode — phone detection is disabled online.")
        # Initialize a session state variable
    if "simulate_alert" not in st.session_state:
        st.session_state.simulate_alert = False
        # Button to simulate detection
    if st.button("Simulate Phone Detection"):
        st.session_state.simulate_alert = True
        # Show alert if session_state is True
    if st.session_state.simulate_alert:
        alert.warning("📱 Phone detected! Put it away!")
    else:
            # Run full local detection
            start_time = time.time()
            for phone_detected in run_detection():
                elapsed = (time.time() - start_time) / 60  # in minutes
                if elapsed >= focus_time:
                    st.success("Focus session completed! 🎉")
                    break

                if phone_detected:
                    alert.warning("📱 Phone detected! Put it away!")
                    play_alert()
                    time.sleep(1)  # avoid spam
                else:
                    alert.empty()

# ---------------- About Page ----------------
if menu == "About":
    st.header("About Page")
    st.markdown(
        "I'm an ADHD student who struggles with focus during learning. "
        "This results in poor academic performance and stress, especially with distractions like a phone. "
        "FocusEye helps you stay on track!"
    )

# ---------------- Code Page ----------------
if menu == "Code":
    st.header("Code Page")
    st.subheader("Check out how FocusEye detection works")
    st.markdown("<h3 style='text-align:center;'>📷 FocusEye Detection Code</h3>", unsafe_allow_html=True)
    code = '''
from ultralytics import YOLO
import cv2

# Load YOLOv8 model trained on COCO
model = YOLO("yolov8n.pt")
PHONE_CLASS_ID = 67

def run_detection():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = model(frame, classes=[PHONE_CLASS_ID])
            phone_detected = any(int(cls) == PHONE_CLASS_ID for cls in results[0].boxes.cls)
            yield phone_detected
    finally:
        cap.release()
    '''
    st.code(code, language="python")

# ---------------- Feedback ----------------
st.header("Rate My Project")
user_reply = st.chat_input("Leave a comment or rating about my project:")
if user_reply:
    st.chat_message("user").write(user_reply)
    st.feedback("stars")
