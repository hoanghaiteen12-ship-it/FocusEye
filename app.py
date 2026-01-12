# app.py
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from ultralytics import YOLO
import cv2
import numpy as np
import os
import time
from threading import Thread

# ---------------- ENVIRONMENT CHECK ----------------
DEMO_MODE = st.runtime.exists() is False  # True if running online without local webcam

# ---------------- SOUND ALERT ----------------
def play_alert():
    if not DEMO_MODE:
        os.system("afplay alertsound.mp3 &")  # Works on Mac locally

# ---------------- PAGE TITLE ----------------
st.markdown("<h1 style='text-align:center; color:#00BFFF;'>FocusEye</h1>", unsafe_allow_html=True)

# ---------------- MENU ----------------
menu = option_menu("Main Menu", ["Home", "About", "Code"],
                   icons=['house', 'info-circle', 'code-slash'], menu_icon="cast", default_index=0)

# ---------------- HOME PAGE ----------------
if menu == "Home":
    st.header("Home Page")
    st.markdown("FocusEye helps you stay focused by detecting your phone and warning you if you get distracted.")

    # Focus session input
    focus_minutes = st.number_input("Set your focus session (minutes):", min_value=1, max_value=180, value=25)
    start = st.button("Start Focus Session")

    # Placeholder for alert messages
    alert_placeholder = st.empty()

    if start:
        st.success(f"Focus session started for {focus_minutes} minutes!")
        session_start = time.time()
        session_seconds = focus_minutes * 60

        if DEMO_MODE:
            st.warning("Running in Demo Mode — no webcam detected.")
            # Simulate detection in demo mode
            simulate_btn = st.button("Simulate Phone Detection")
            if simulate_btn:
                alert_placeholder.warning("📱 Phone detected! Put it away!")

        else:
            # ---------------- YOLO MODEL ----------------
            model = YOLO("yolov8n.pt")
            PHONE_CLASS_ID = 67

            # ---------------- Video Transformer ----------------
            class PhoneDetector(VideoTransformerBase):
                def __init__(self):
                    self.last_alert = 0  # prevent spamming

                def transform(self, frame):
                    img = frame.to_ndarray(format="bgr24")
                    results = model(img, classes=[PHONE_CLASS_ID])
                    annotated = results[0].plot()

                    # ---------------- PHONE ALERT ----------------
                    phone_detected = any(int(cls) == PHONE_CLASS_ID for cls in results[0].boxes.cls)
                    if phone_detected and time.time() - self.last_alert > 1:  # 1 sec cooldown
                        Thread(target=play_alert).start()
                        self.last_alert = time.time()
                        # Update Streamlit alert in main thread
                        alert_placeholder.warning("📱 Phone detected! Put it away!")

                    # ---------------- TIMER OVERLAY ----------------
                    elapsed = int(time.time() - session_start)
                    remaining = max(0, session_seconds - elapsed)
                    mins = remaining // 60
                    secs = remaining % 60
                    timer_text = f"⏳ Focus Time Left: {mins:02d}:{secs:02d}"
                    cv2.putText(annotated, timer_text, (50, annotated.shape[0]-50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                    if remaining == 0:
                        cv2.putText(annotated, "🎉 Focus Session Complete!", (50, annotated.shape[0]//2),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)

                    return annotated

            # ---------------- START WEBCAM ----------------
            if "webrtc_started" not in st.session_state:
                st.session_state.webrtc_started = True
                webrtc_streamer(
                    key="phone-detector",
                    video_transformer_factory=PhoneDetector,
                    media_stream_constraints={"video": True, "audio": False},
                )

# ---------------- ABOUT PAGE ----------------
elif menu == "About":
    st.header("About FocusEye")
    st.markdown("""
    FocusEye helps students and learners stay focused by detecting when a phone appears in view.
    It provides real-time alerts and tracks focus sessions with a countdown timer.
    """)

# ---------------- CODE PAGE ----------------
elif menu == "Code":
    st.header("Detection Code")
    st.code('''
from ultralytics import YOLO
import cv2
from streamlit_webrtc import VideoTransformerBase

model = YOLO("yolov8n.pt")
PHONE_CLASS_ID = 67

class PhoneDetector(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        results = model(img, classes=[PHONE_CLASS_ID])
        phone_detected = any(int(cls)==PHONE_CLASS_ID for cls in results[0].boxes.cls)
        annotated = results[0].plot()
        if phone_detected:
            cv2.putText(annotated, "📱 Phone Detected!", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return annotated
    ''', language="python")

# ---------------- FEEDBACK ----------------
st.header("Rate My Project")
user_reply = st.chat_input("Leave a comment or rate my project ⭐:")
if user_reply:
    st.chat_message("user").write(user_reply)
    st.feedback("stars")
