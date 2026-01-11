# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import os
import time

# ---------------- ENVIRONMENT DETECTION ----------------
DEMO_MODE = os.environ.get("STREAMLIT_DEMO", "false").lower() == "true"

try:
    if not DEMO_MODE:
        from FocusEye import run_detection  # real YOLO detection
except Exception:
    DEMO_MODE = True

# ---------------- SOUND ALERT FUNCTION (macOS only) ----------------
def play_alert():
    if not DEMO_MODE:
        os.system("afplay alertsound.mp3 &")  # plays in background

# ---------------- PAGE TITLE ----------------
st.markdown("<h1 style='text-align:center; color:#00BFFF;'>FocusEye</h1>", unsafe_allow_html=True)

# ---------------- MENU ----------------
menu = option_menu("Main Menu", ["Home", "About", "Code"],
                   icons=['house', 'info-circle', 'code-slash'], menu_icon="cast", default_index=0)

# ---------------- HOME PAGE ----------------
if menu == "Home":
    st.header("Home Page")
    st.markdown("FocusEye helps you stay focused by detecting your phone and warning you when you get distracted.")

    focus_time = st.number_input("Set focus session (minutes)", min_value=1, max_value=180, value=25)
    start = st.button("Start Focus Session")

    alert = st.empty()  # placeholder for alerts

    if start:
        st.success(f"Focus session started for {focus_time} minutes! Stay focused and avoid distractions.")

        if DEMO_MODE:
            st.warning("Running in Demo Mode — phone detection is disabled online.")

            # --------- Demo Mode Simulation ----------
            if "simulate_alert" not in st.session_state:
                st.session_state.simulate_alert = False

            if st.button("Simulate Phone Detection"):
                st.session_state.simulate_alert = True

            if st.session_state.simulate_alert:
                alert.warning("📱 Phone detected! Put it away!")

        else:
            # --------- Full Mode ----------
            start_time = time.time()
            for phone_detected in run_detection():
                elapsed = (time.time() - start_time) / 60
                if elapsed >= focus_time:
                    st.success("Focus session completed! 🎉")
                    break

                if phone_detected:
                    alert.warning("📱 Phone detected! Put it away!")
                    play_alert()
                    time.sleep(1)  # prevent alert spam
                else:
                    alert.empty()

# ---------------- ABOUT PAGE ----------------
elif menu == "About":
    st.header("About FocusEye")
    st.markdown("""
    I'm an ADHD student who struggles with focus during learning.  
    FocusEye helps me stay accountable by detecting when my phone is nearby  
    and warning me in real-time to stay focused on my study.
    """)

# ---------------- CODE PAGE ----------------
elif menu == "Code":
    st.header("Detection Code (Simplified)")
    st.subheader("Core logic from FocusEye.py")
    st.code('''
from ultralytics import YOLO
import cv2

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
    ''', language="python")

# ---------------- FEEDBACK SECTION ----------------
st.header("Rate My Project")
user_reply = st.chat_input("Leave a comment or rate my project ⭐:")
if user_reply:
    st.chat_message("user").write(user_reply)
    st.feedback("stars")
