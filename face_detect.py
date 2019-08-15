# MIT License
# Copyright (c) 2019 JetsonHacks
# See LICENSE for OpenCV license and additional information

# https://docs.opencv.org/3.3.1/d7/d8b/tutorial_py_face_detection.html
# On the Jetson Nano, OpenCV comes preinstalled
# Data files are in /usr/sharc/OpenCV
import numpy as np
import cv2
import time

import ev3
import ev3_vehicle

vehicle = ev3_vehicle.TwoWheelVehicle(
    0.02128,                 # radius_wheel
    0.1175,                  # tread
    protocol=ev3.constants.USB,
)

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 30fps 
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen

def gstreamer_pipeline (capture_width=3280, capture_height=2464, display_width=820, display_height=616, framerate=21, flip_method=0):   
    return ('nvarguscamerasrc ! ' 
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

def face_detect():
    face_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_eye.xml')
    cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        # cv2.namedWindow('Face Detect', cv2.WINDOW_AUTOSIZE)
        try:
            while True:  # cv2.getWindowProperty('Face Detect',0) >= 0:
                ret, img = cap.read()

                gh, gw = img.shape[:2]
                gmx, gmy = int(gw / 2), int(gh / 2)
                # cv2.rectangle(img, (gmx - 5, gmy - 5), (gmx + 5, gmy + 5), (255, 0, 0), 2)

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                #import ipdb; ipdb.set_trace()
                #for (x,y,w,h) in faces:
                # only use the first face
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    mx, my = (2*x + w) / 2, (2*y + h) / 2
                    mx, my = int(mx), int(my)

                    area = w * h
                    #print(f"AREA: {area}")
                    if area < 60000:
                        speed = 25
                        if ((x < gmx < x + w) and (y < gmy < y + h)):
                            if mx < gmx:
                                vehicle._drive_turn(speed, 0.25, 60, True)
                            if my > gmy:
                                vehicle._drive_turn(-speed, 0.25, 60, True)
                            else:
                                vehicle._drive_straight(speed, None)
                        time.sleep(0.5)
                        vehicle.stop()

                    dx = gmx - mx
                    dy = gmy - my

                    # if abs(dx) > tol:
                    #     print(f"moving dx {dx}")

                    # if abs(dy) > tol:
                    #     print(f"moving dy {dy}")

                    # cv2.rectangle(img, (mx - 1, my - 1), (mx + 1, my + 1), (0, 255, 0), 2)
                    #roi_gray = gray[y:y+h, x:x+w]
                    #roi_color = img[y:y+h, x:x+w]
                    #eyes = eye_cascade.detectMultiScale(roi_gray)
                    #for (ex,ey,ew,eh) in eyes:
                        #cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

                # cv2.imshow('Face Detect', img)
                # keyCode = cv2.waitKey(30) & 0xff
                # Stop the program on the ESC key
                # if keyCode == 27:
                    # break
        except Exception:
            pass

        finally:
            cap.release()
            cv2.destroyAllWindows()
    else:
        print("Unable to open camera")

if __name__ == '__main__':
    face_detect()
