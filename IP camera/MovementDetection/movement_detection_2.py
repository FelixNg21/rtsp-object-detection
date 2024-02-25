# https://www.kdnuggets.com/2022/08/perform-motion-detection-python.html
import sys

import pandas as panda
import cv2
import time
from imutils.video import VideoStream
from datetime import datetime

initialState = None
motionTrackList = [None, None]
motionTime = []
dataFrame = panda.DataFrame(columns=["Initial", "Final"])

fourcc = cv2.VideoWriter.fourcc(*'mp4v')

# try:
#     url = "rtsp://localhost:8554/driveway"
#     video = VideoStream(url).start()
#     curr_frame = video.read()
# except cv2.error:
#     video_path = "/test_footage.mp4"
#     video = cv2.VideoCapture(video_path)
#     check, curr_frame = video.read()

video_path = "test_footage.mp4"
video = cv2.VideoCapture(video_path)
frame_width = int(video.get(3))
frame_height = int(video.get(4))
frame_size = (frame_width,frame_height)
record = False
fps= video.get(cv2.CAP_PROP_FPS)
spf = int(1/fps * 1000)


sta = 0
while video.isOpened():
    ret, curr_frame = video.read()
    var_motion = 0
    gray_image = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.GaussianBlur(gray_image, (21, 21), 0)
    if initialState is None:
        initialState = gray_image
        continue

    diff_frame = cv2.absdiff(initialState, gray_image)

    threshold_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)

    (contours, _) = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 100:
            record = False
            continue
        var_motion = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(curr_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        record = True

    motionTrackList.append(var_motion)
    motionTrackList = motionTrackList[-2:]

    if motionTrackList[-1] == 1 and motionTrackList[-2] == 0:
        motionTime.append(datetime.now())

    if motionTrackList[-1] == 0 and motionTrackList[-2] == 1:
        motionTime.append(datetime.now())

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
                filename = 'video-' + st + '.mp4'
                out = cv2.VideoWriter(filename, fourcc, fps, frame_size)
                sta = st
            out.write(curr_frame)
        except Exception as e:
            print(f'Error on line {sys.exc_info()[-1].tb_lineno}', type(e).__name__, e)


    if waitKey == ord('q'):
        if var_motion == 1:
            motionTime.append(datetime.now())
        break

# Releasing the video
video.release()

# Now, Closing or destroying all the open windows with the help of openCV
cv2.destroyAllWindows()