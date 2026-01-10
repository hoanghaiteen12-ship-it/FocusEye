from torch import classes
from ultralytics import YOLO
import cv2
import numpy as np

#Load the YOLO model
model = YOLO('yolov8n.pt')
#Make a new function to call:
def run_detection():
    cap = cv2.VideoCapture(0)
    #Properties of the frame
    h = int(cap.get(4))
    w = int(cap.get(3))
    while True:
        ret,frame = cap.read()
        if not ret:
            print("The camera is not working")
            break
        
        results = model(frame, classes = [67]) #--> Creating a new numpy array from the org img to detect objects
        phone_detected = False
        #Display the result on the image
        annotated_frame = results[0].plot() #Draw boxes around the objects
        #Specific Object Detection
        for result in results: #-->Looping through each images in the batch.
            for box,cls,conf in zip(result.boxes.xyxy,result.boxes.cls,result.boxes.conf):
                print(f"The coordinate of the object is: {box}")
                print(f"The class of the detected object is {int(cls)}")
                print(f"The confidence score of the YOLO algo is: {conf.item()}") #Use .item() to convert Tensor value to normal float value
                if int(cls) == 67:
                    print('Phone Detected!')
                    phone_detected = True
                    break
        yield phone_detected
    cap.release()
