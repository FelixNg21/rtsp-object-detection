import sys
import multiprocessing
import signal
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from collections import defaultdict

from frame_processor import FrameProcessor
from frame_tracker import FrameTracker


def track_history_default():
    return []


class MotionDetector:
    def __init__(self, cap, movement_threshold, delay_time, video_writer, model_name):
        self.cap = cap
        self.track_history = defaultdict(track_history_default)
        self.model = YOLO(model_name)
        self.names = self.model.names
        self.model_name = model_name

        self.frame_queue = queue.Queue(maxsize=90)
        self.results_queue = queue.Queue(maxsize=90)
        self.video_writer = video_writer

        self.queue_event = threading.Event()
        self.frame_processor = FrameProcessor(cap, self.frame_queue, self.results_queue, self.process_single_frame,
                                              self.queue_event)
        self.frame_tracker = FrameTracker(cap, self.results_queue, self.video_writer, self.track_movement_history,
                                          self.plot_tracks, self.write_frame, self.track_history, self.queue_event)
        self.frame_getter = threading.Thread(target=self.get_frame)

        self.movement_threshold = movement_threshold
        self.motion_stop_time = None
        self.delay_time = delay_time

        signal.signal(signal.SIGTERM, self.signal_handler)

    def run(self):
        """
        Run the camera object detection process.

        Returns:
            None
        """
        self.frame_getter.start()
        self.frame_processor.start()
        self.frame_tracker.start()

    def get_frame(self):
        """
        Capture frames from an RTSP stream and put them into a frame queue.

        Returns:
            None
        """
        while self.cap.isOpened():
            success, frame_high_quality = self.cap.read()
            if success:
                self.frame_queue.put(frame_high_quality)

    def process_single_frame(self, frame_high_quality):
        """
        Process a single frame by tracking objects, handling tracking results, and writing frames if recording.

        Args:
            frame_high_quality: The high-quality frame to process.

        Returns:
            None
        """
        model = YOLO(self.model_name)
        return model.track(frame_high_quality, persist=True, verbose=False), frame_high_quality

    def track_frame(self):
        """
        Track the results from the frame queue.

        Returns:
            None
        """
        while not self.results_queue.empty() or self.cap.isOpened():
            results = self.results_queue.get()
            self.handle_tracking(results[1])
            if self.video_writer.recording:
                cv2.imshow("frame", results[0])
                cv2.waitKey(1)
                self.write_frame(results[0])
            else:
                print("Results queue empty")

    def handle_tracking(self, results):
        """
        Handle tracking results by annotating the frame with object labels and colors,
        storing tracking history, and plotting tracks if sufficient history is available.

        Args:
            frame: The frame to annotate.
            results: The tracking results to process.

        Returns:
            None
        """

        boxes = results[0].boxes.xyxy.cpu()
        if results[0].boxes.id is not None:
            # Extract prediction results
            clss = results[0].boxes.cls.cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, cls, track_id in zip(boxes, clss, track_ids):
                self.track_movement_history(track_id, box)
                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track_id)

    def write_frame(self, frame):
        """
        Write a frame to the video writer.

        Args:
            frame: The frame to write.

        Returns:
            None
        """
        self.video_writer.write_frame(frame)

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

    def plot_tracks(self, track_id):
        """
        Calculate displacement between previous and current track centers,
        start or stop recording based on movement threshold and recording status.

        Args:
            track_id: The identifier of the track to process.

        Returns:
            None
        """
        prev_center = self.track_history[track_id][-2]
        current_center = self.track_history[track_id][-1]
        displacement = np.sqrt(
            (prev_center[0] - current_center[0]) ** 2 + (prev_center[1] - current_center[1]) ** 2)

        # Plot tracks if sufficient movement
        if displacement > self.movement_threshold:
            if not self.video_writer.recording:
                self.video_writer.start_recording()
            self.motion_stop_time = time.time()

        if displacement < self.movement_threshold and self.video_writer.recording:
            if self.motion_stop_time is None:
                self.motion_stop_time = time.time()
            elif (time.time() - self.motion_stop_time) > self.delay_time:
                self.video_writer.stop_recording()
                self.track_history.clear()
                self.motion_stop_time = None

    def signal_handler(self, signum, frame):
        """
        Signal handler for SIGTERM.
        """
        print("Shutting down")
        self.cleanup()
        sys.exit()

    def cleanup(self):
        """
        Clean up the camera object detection process.
        """

        if self.cap is not None:
            self.cap.release()
            self.frame_tracker.join()
            self.frame_processor.join()
            self.frame_getter.join()
        self.video_writer.cleanup()
