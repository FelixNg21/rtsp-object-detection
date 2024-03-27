# adapted from: https://colab.research.google.com/github/ultralytics/ultralytics/blob/main/examples/object_tracking.ipynb
# adapted from: https://colab.research.google.com/github/ultralytics/ultralytics/blob/main/examples/object_tracking.ipynb
import datetime
import time

import cv2
import numpy as np
from ultralytics import YOLO

from ultralytics.utils.checks import check_imshow
from ultralytics.utils.plotting import Annotator, colors

from collections import defaultdict

track_history = defaultdict(lambda: [])
model = YOLO("yolov8n.pt")
names = model.model.names

rtsp_url = "rtsp://localhost:8554/driveway"
cap = cv2.VideoCapture(rtsp_url)
assert cap.isOpened(), "Error reading video stream"

w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

recording = False
video_writer = None

movement_threshold = 20 #pixels
motion_stop_time = None
delay_time = 5

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    results = model.track(frame, persist=True, verbose=False)
    boxes = results[0].boxes.xyxy.cpu()

    if results[0].boxes.id is not None:
        # Extract prediction results
        clss = results[0].boxes.cls.cpu().tolist()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # Annotator Init
        annotator = Annotator(frame, line_width=2)

        for box, cls, track_id in zip(boxes, clss, track_ids):
            annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])

            # Store tracking history
            track = track_history[track_id]
            current_position = (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2))
            track.append(current_position)
            if len(track) > 30:
                track.pop(0)

            if len(track_history[track_id]) >= 2:
                prev_center = track_history[track_id][-2]
                current_center = track_history[track_id][-1]
                displacement = np.sqrt((prev_center[0] - current_center[0])**2 + (prev_center[1] - current_center[1])**2)

                # Plot tracks if sufficient movement
                if displacement > movement_threshold:
                    points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.circle(frame, (track[-1]), 7, colors(int(cls), True), -1)
                    cv2.polylines(frame, [points], isClosed=False, color=colors(int(cls), True), thickness=2)

                    if not recording:
                        now = datetime.datetime.now()
                        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
                        filename = f"{now_str}.mp4"
                        video_writer = cv2.VideoWriter(filename,
                                                       cv2.VideoWriter_fourcc(*'mp4v'),
                                                       fps,
                                                       (w, h))
                        recording = True
                        motion_stop_time = None

                elif recording:
                    if motion_stop_time is None:
                        motion_stop_time = time.time()
                    else:
                        if (time.time() - motion_stop_time) >= delay_time:
                            recording = False
                            video_writer.release()
                            motion_stop_time = None
                            track_history.clear()

    if recording:
        video_writer.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

if recording:
    video_writer.release()

cap.release()
cv2.destroyAllWindows()