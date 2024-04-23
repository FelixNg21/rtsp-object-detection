# adapted from: https://colab.research.google.com/github/ultralytics/ultralytics/blob/main/examples/object_tracking.ipynb

import datetime
import os
import threading
import multiprocessing
import time
import queue
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

from collections import defaultdict

import file_manager


class MotionDetector:

    def __init__(self, rtsp_url, movement_threshold, delay_time, video_dir, model_path="yolov8n.pt",
                 file_manager=None):
        """
        Args:
            rtsp_url (str): The RTSP URL of the IP camera stream.
            movement_threshold (int): The threshold for detecting movement in consecutive frames.
            delay_time (int): The delay time in seconds before ending recording.

        Returns:
            None
        """
        self.cap = None
        self.track_history = defaultdict(self.track_history_default)
        self.model = YOLO(model_path)
        self.names = self.model.names

        self.rtsp_url = rtsp_url
        self.h_high, self.w_high, self.fps = (multiprocessing.Value('i', 0),
                                              multiprocessing.Value('i', 0),
                                              multiprocessing.Value('i', 0))

        # self.cap_high_res = cv2.VideoCapture(rtsp_url)
        #
        # assert self.cap_high_res.isOpened(), f"Failed to open {rtsp_url}"
        #
        # self.w_high, self.h_high, self.fps = (int(self.cap_high_res.get(x)) for x in
        #                                       (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

        self.frame_queue = multiprocessing.Queue()
        self.video_dir = video_dir
        self.recording = False
        self.video_writer = None

        self.movement_threshold = movement_threshold
        self.motion_stop_time = None
        self.delay_time = delay_time

        # self.file_manager = file_manager

    def track_history_default(self):
        return []

    def start_recording(self):
        """
        Starts recording the video stream from the IP camera.

        Returns:
            None
        """
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        dir_structure = now.strftime("%Y/%m/%d")
        dirname = f"{self.video_dir}/{dir_structure}"
        filename = f"{dirname}/{now_str}.mp4"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        print(f"Recording to {filename}")
        self.video_writer = cv2.VideoWriter(filename,
                                            cv2.VideoWriter_fourcc(*'mp4v'),
                                            int(self.fps.value),
                                            (int(self.w_high.value), int(self.h_high.value)))
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

    def get_frame(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        assert cap.isOpened(), f"Failed to open {self.rtsp_url}"

        if self.h_high.value == 0:
            w_high, h_high, fps = (int(cap.get(x)) for x in
                                   (cv2.CAP_PROP_FRAME_WIDTH,
                                    cv2.CAP_PROP_FRAME_HEIGHT,
                                    cv2.CAP_PROP_FPS))
            with self.h_high.get_lock():
                self.h_high.value = h_high
            with self.w_high.get_lock():
                self.w_high.value = w_high
            with self.fps.get_lock():
                self.fps.value = fps

        while cap.isOpened():
            success, frame_high_quality = cap.read()
            if success:
                self.frame_queue.put(frame_high_quality)

    def process_frame(self):
        while True:
            try:
                frame_high_quality = self.frame_queue.get()
            except queue.Empty:
                print("Queue empty")
                continue
            results = self.model.track(frame_high_quality, persist=True, verbose=False)
            self.handle_tracking(frame_high_quality, results)
            if self.recording:
                self.write_frame(frame_high_quality)

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
                self.track_movement_history(track_id, box)

                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track_id)

    def plot_tracks(self, track_id):
        prev_center = self.track_history[track_id][-2]
        current_center = self.track_history[track_id][-1]
        displacement = np.sqrt(
            (prev_center[0] - current_center[0]) ** 2 + (prev_center[1] - current_center[1]) ** 2)

        # Plot tracks if sufficient movement
        if displacement > self.movement_threshold and not self.recording:
            self.start_recording()

        if self.recording:
            if self.motion_stop_time is None:
                self.motion_stop_time = time.time()
            elif (time.time() - self.motion_stop_time) > self.delay_time:
                print("Stopping recording")
                self.stop_recording()

    def write_frame(self, frame):
        self.video_writer.write(frame)

    def run2(self):
        get_frame_thread = multiprocessing.Process(target=self.get_frame)
        process_frame_thread = multiprocessing.Process(target=self.process_frame)

        process_frame_thread.start()
        get_frame_thread.start()

        get_frame_thread.join()
        process_frame_thread.join()

        cv2.destroyAllWindows()


# Usage
if __name__ == "__main__":
    model_path = "yolov8s.pt"
    movement_threshold = 20
    delay_time = 20
    # url = "rtsp://wyze-bridge:8554/driveway"
    url = "rtsp://localhost:8554/driveway"

    # Clean up video files older than 7 days
    video_dir = "videos"
    days_threshold = 7
    file_manager = file_manager.FileManager(video_dir, days_threshold)

    motion_detector = MotionDetector(url, movement_threshold, delay_time, video_dir, model_path,
                                     file_manager)
    motion_detector.run2()
    cv2.destroyAllWindows()
