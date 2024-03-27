# adapted from: https://colab.research.google.com/github/ultralytics/ultralytics/blob/main/examples/object_tracking.ipynb
import datetime
import time

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from collections import defaultdict


class MotionDetector:

    def __init__(self, rtsp_url, movement_threshold, delay_time):
        """
        Args:
            rtsp_url (str): The RTSP URL of the IP camera stream.
            movement_threshold (int): The threshold for detecting movement in consecutive frames.
            delay_time (int): The delay time in seconds before ending recording.

        Returns:
            None
        """
        self.track_history = defaultdict(lambda: [])
        self.model = YOLO("yolov8n.pt")
        self.names = self.model.model.names

        self.cap = cv2.VideoCapture(rtsp_url)
        assert self.cap.isOpened(), "Error reading video stream"

        self.w, self.h, self.fps = (int(self.cap.get(x)) for x in
                                    (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

        self.recording = False
        self.video_writer = None

        self.movement_threshold = movement_threshold
        self.motion_stop_time = None
        self.delay_time = delay_time

    def start_recording(self):
        """
        Starts recording the video stream from the IP camera.

        Returns:
            None
        """
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{now_str}.mp4"
        self.video_writer = cv2.VideoWriter(filename,
                                            cv2.VideoWriter_fourcc(*'mp4v'),
                                            self.fps,
                                            (self.w, self.h))
        self.recording = True
        self.motion_stop_time = None

    def stop_recording(self):
        """
        Stops the recording of the video stream from the IP camera.

        Returns:
            None
        """
        self.recording = False
        self.video_writer.release()
        self.motion_stop_time = None
        self.track_history.clear()

    def track_movement_history(self, track_id, box):
        """
        Tracks the movement history of an object identified by track_id.

        Args:
            track_id (int): The unique identifier of the tracked object.
            box (tuple): The bounding box coordinates of the object.

        Returns:
            list: The updated movement history of the tracked object.
        """
        # Store tracking history
        track = self.track_history[track_id]
        current_position = (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2))
        track.append(current_position)
        if len(track) > 30:
            track.pop(0)
        return track

    def process_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        results = self.model.track(frame, persist=True, verbose=False)
        return frame, results

    def handle_tracking(self, frame, results):
        boxes = results[0].boxes.xyxy.cpu()
        if results[0].boxes.id is not None:
            # Extract prediction results
            clss = results[0].boxes.cls.cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            # Annotator Init
            annotator = Annotator(frame, line_width=2)

            for box, cls, track_id in zip(boxes, clss, track_ids):
                annotator.box_label(box, color=colors(int(cls), True), label=self.names[int(cls)])

                # Store tracking history
                track = self.track_movement_history(track_id, box)

                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track, track_id, cls, frame)

    def plot_tracks(self, track, track_id, cls, frame):
        prev_center = self.track_history[track_id][-2]
        current_center = self.track_history[track_id][-1]
        displacement = np.sqrt(
            (prev_center[0] - current_center[0]) ** 2 + (prev_center[1] - current_center[1]) ** 2)

        # Plot tracks if sufficient movement
        if displacement > self.movement_threshold:
            points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
            cv2.circle(frame, (track[-1]), 7, colors(int(cls), True), -1)
            cv2.polylines(frame, [points], isClosed=False, color=colors(int(cls), True), thickness=2)

            if not self.recording:
                self.start_recording()

        elif self.recording:
            if self.motion_stop_time is None:
                self.motion_stop_time = time.time()
            elif (time.time() - self.motion_stop_time) > self.delay_time:
                self.stop_recording()

    def write_frame(self, frame):
        if self.recording:
            self.video_writer.write(frame)

    def run(self):
        while self.cap.isOpened():
            frame_results = self.process_frame()
            if frame_results is None:
                break
            frame, results = frame_results
            self.handle_tracking(frame, results)
            self.write_frame(frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if self.recording:
            self.video_writer.release()

        self.cap.release()
        cv2.destroyAllWindows()


# Usage
if __name__ == "__main__":
    movement_threshold = 20
    delay_time = 10
    motion_detector = MotionDetector("rtsp://localhost:8554/driveway", movement_threshold, delay_time)
    motion_detector.run()
