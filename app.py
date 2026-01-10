# app.py
import streamlit as st
from streamlit_option_menu import option_menu
from FocusEye import run_detection
import time
import os 
def playalert():
    os.system(f"afplay /Users/hoanghai/Projects/alertsound.mp3 &")
# --- Title ---
st.markdown("<h1 style='text-align:center; color:#00BFFF;'>FocusEye</h1>", unsafe_allow_html=True)

# --- Menu ---
menu = option_menu("Main Menu", ["Home", "About", "Code"],
                   icons=['house', 'info-circle', 'code-slash'], menu_icon="app-indicator", default_index=0)

# --- Home Page ---
if menu == "Home":
    st.header("Home Page")
    st.markdown("FocusEye helps you stay focused by detecting your phone and warning you when you get distracted.")
    
    focus_time = st.number_input("Set your focus time session (minutes)", min_value=1, max_value=180, value=25)
    start = st.button("Start Focus Session")

    if start:
        st.success(f"Focus session started for {focus_time} minutes! Stay focused and avoid distractions from your phone.")
        alert = st.empty()  # placeholder for live alert messages

        for phone_detected in run_detection():
            if phone_detected:
                alert.warning("📱 Phone detected! Put it away!")
                playalert()
                time.sleep(1)  # small delay to avoid spamming
            else:
                alert.empty()

# --- About Page ---
elif menu == "About":
    st.header("About FocusEye")
    st.markdown("""
    I'm an ADHD student who struggles with distractions during study.
    To improve focus, I developed **FocusEye**, an app that detects when
    your phone is nearby and warns you instantly — helping you stay on track.
    """)

# --- Code Page ---
elif menu == "Code":
    st.header("Detection Code (Simplified)")
    code = '''
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")
PHONE_CLASS_ID = 67

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame, classes=[PHONE_CLASS_ID])
    if any(int(cls) == PHONE_CLASS_ID for cls in results[0].boxes.cls):
        print("Phone detected!")
cap.release()
'''
    st.code(code, language="python")