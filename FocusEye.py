# FocusEye.py
from ultralytics import YOLO
import cv2

# Load YOLOv8 model trained on COCO
model = YOLO("yolov8n.pt")
PHONE_CLASS_ID = 67  # 'cell phone' class

def run_detection():
    """
    Continuously captures webcam frames and detects phones.
    Yields True if a phone is detected, False otherwise.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Cannot read frame")
                break

            # Run YOLO only for phone class
            results = model(frame, classes=[PHONE_CLASS_ID])
            phone_detected = any(int(cls) == PHONE_CLASS_ID for cls in results[0].boxes.cls)

            # Yield True (detected) or False (no phone)
            yield phone_detected

    finally:
        cap.release()