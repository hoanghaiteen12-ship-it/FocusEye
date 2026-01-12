import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from ultralytics import YOLO
import cv2
import time
import os

# Load YOLO model
model = YOLO("yolov8n.pt")
PHONE_CLASS_ID = 67

# Sound alert
def play_alert():
    os.system("afplay alertsound.mp3 &")  # macOS sound alert


# UI input for focus session
st.title("🎯 FocusEye Live Detection")
focus_time = st.number_input("Set your focus time (minutes):", min_value=1, max_value=180, value=25)
start = st.button("Start Focus Session")

if start:
    st.success(f"Focus session started for {focus_time} minutes!")
    st.info("Keep your phone away and stay focused 👀")

    session_start = time.time()
    session_seconds = focus_time * 60

    # ---------------- Video Transformer ----------------
    class PhoneDetector(VideoTransformerBase):
        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")

            # Run YOLO phone detection
            results = model(img, classes=[PHONE_CLASS_ID])
            phone_detected = any(int(cls) == PHONE_CLASS_ID for cls in results[0].boxes.cls)
            annotated = results[0].plot()

            # Display warning if phone is detected
            if phone_detected:
                cv2.putText(
                    annotated, "📱 Phone Detected!", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
                )
                play_alert()

            # Calculate time left
            elapsed = int(time.time() - session_start)
            remaining = max(0, session_seconds - elapsed)
            mins = remaining // 60
            secs = remaining % 60

            # Overlay countdown timer
            timer_text = f"⏳ Focus Time Left: {mins:02d}:{secs:02d}"
            cv2.putText(
                annotated, timer_text, (50, annotated.shape[0] - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )

            # Session completed message
            if remaining == 0:
                cv2.putText(
                    annotated, "🎉 Focus Session Complete!", (50, annotated.shape[0] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3
                )

            return annotated

    # ---------------- Start Webcam Stream ----------------
    webrtc_streamer(
        key="phone-detector",
        video_transformer_factory=PhoneDetector,
        media_stream_constraints={"video": True, "audio": False},
    )
