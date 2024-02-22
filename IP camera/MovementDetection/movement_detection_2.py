# https://www.kdnuggets.com/2022/08/perform-motion-detection-python.html

import pandas as panda
import cv2
import time
from imutils.video import VideoStream
from datetime import datetime

initialState = None
motionTrackList = [None, None]
motionTime = []
dataFrame = panda.DataFrame(columns=["Initial", "Final"])
url = "rtsp://localhost:8554/driveway"
video = VideoStream(url).start()

while True:
    curr_frame = video.read()
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
        if cv2.contourArea(contour) < 10000:
            continue
        var_motion = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(curr_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

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
    waitKey = cv2.waitKey(1)

    if waitKey == ord('q'):
        if var_motion == 1:
            motionTime.append(datetime.now())
        break

# At last we are adding the time of motion or var_motion inside the data frame
for a in range(0, len(motionTime), 2):
    dataFrame = dataFrame.append({"Initial": time[a], "Final": motionTime[a + 1]}, ignore_index=True)

# To record all the movements, creating a CSV file
dataFrame.to_csv("EachMovement.csv")

# Releasing the video
video.release()

# Now, Closing or destroying all the open windows with the help of openCV
cv2.destroyAllWindows()