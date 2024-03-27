# https://www.kdnuggets.com/2022/08/perform-motion-detection-python.html
import sys
import cv2
import time
import numpy as np
from datetime import datetime

initialState = None

try:
    url = "rtsp://localhost:8554/driveway"
    video = cv2.VideoCapture(url)
except cv2.error:
    video_path = "/test_footage.mp4"
    video = cv2.VideoCapture(video_path)

# Defining the codec and creating VideoWriter object
fourcc = cv2.VideoWriter.fourcc(*'mp4v')
fps = video.get(cv2.CAP_PROP_FPS)
record = False

# Getting the frame width and height then creating a frame size tuple
frame_width = int(video.get(3))
frame_height = int(video.get(4))
frame_size = (frame_width,frame_height)
spf = int(1/fps * 1000)

# Function for background subtraction using GMM
def background_subtraction(frame, bg_model, learning_rate):
    fg_mask = bg_model.apply(frame)
    _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
    return fg_mask

# Initialize background model and learning rate
bg_model = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=20, detectShadows=True)
learning_rate = 0.01

sta = 0
while video.isOpened():
    try:
        ret, curr_frame = video.read()
    except Exception:
        curr_frame = video.read()
    gray_image = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    # Apply background subtraction
    fg_mask = background_subtraction(gray_image, bg_model, learning_rate)

    # Apply thresholding
    threshold_frame = cv2.adaptiveThreshold(fg_mask, 127, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11,2)

    gray_image = cv2.GaussianBlur(gray_image, (21, 21), 0)
    if initialState is None:
        initialState = gray_image
        continue

    diff_frame = cv2.absdiff(initialState, gray_image)

    (contours, _) = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 100:
            record = False
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(curr_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        record = True

    cv2.imshow("Gray Frame", gray_image)
    cv2.imshow("Difference Frame", diff_frame)
    cv2.imshow("Threshold Frame", threshold_frame)
    cv2.imshow("Color Frame", curr_frame)
    waitKey = cv2.waitKey(delay=spf)

    if record:
        try:
            ts = time.time()
            st = datetime.fromtimestamp(ts).strftime("%Y.%m.%d_%H-%M")
            if sta != st:
                filename = f'video-{st}.mp4'
                out = cv2.VideoWriter(filename, fourcc, fps, frame_size)
                sta = st
            out.write(curr_frame)
        except Exception as e:
            print(f'Error on line {sys.exc_info()[-1].tb_lineno}', type(e).__name__, e)

    if waitKey == ord('q'):
        break

# Releasing the video
video.release()

# Now, Closing or destroying all the open windows with the help of openCV
cv2.destroyAllWindows()