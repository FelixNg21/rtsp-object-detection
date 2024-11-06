import logging
import sys
import signal
import threading
import queue

from collections import defaultdict, deque

from detection.frame_processor_threaded import FrameProcessor
from detection.frame_tracker_threaded import FrameTracker


def track_history_default():
    return deque(maxlen=30)


class MotionDetector:
    def __init__(self, cap, movement_threshold, delay_time, video_writer, model_name):
        self.cap = cap
        self.track_history = defaultdict(track_history_default)
        self.model_name = model_name
        self.frame_queue = queue.Queue(maxsize=90)
        self.results_queue = queue.Queue(maxsize=90)
        self.video_writer = video_writer

        self.movement_threshold = movement_threshold
        self.motion_stop_time = None
        self.delay_time = delay_time

        self.queue_event = threading.Event()

        self.frame_processor = FrameProcessor(self.cap, self.frame_queue, self.results_queue,
                                              self.queue_event, self.model_name)

        self.frame_tracker = FrameTracker(self.results_queue, self.video_writer, self.track_movement_history,
                                          self.write_frame, self.track_history, self.queue_event, self.motion_stop_time,
                                          self.delay_time, self.movement_threshold)
        self.frame_getter = threading.Thread(target=self.get_frame)

        self.shutdown_flag = threading.Event()
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def run(self):
        """
        Run the camera object detection process.

        Returns:
            None
        """
        self.frame_getter.start()
        self.frame_processor.start()
        self.frame_tracker.start()

        self.frame_processor.join()
        self.frame_getter.join()
        self.frame_tracker.join()

    def get_frame(self):
        """
        Capture frames from an RTSP stream and put them into a frame queue.

        Returns:
            None
        """
        while self.cap.isOpened() and not self.shutdown_flag.is_set():
            success, frame_high_quality = self.cap.read()
            if success:
                try:
                    self.frame_queue.put(frame_high_quality, timeout=1)
                except queue.Full:
                    logging.warning("Frame queue is full. Skipping frame.")

    def write_frame(self, frame):
        """
        Write a frame to the video writer.

        Args:
            frame: The frame to write to video.
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

    def signal_handler(self, signum, frame):
        """
        Signal handler for SIGTERM.
        """
        print("Shutting down")
        self.shutdown_flag.set()

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
