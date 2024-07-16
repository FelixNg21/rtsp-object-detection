import threading
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
import torch
import time


class FrameProcessor(threading.Thread):
    """
       A class for processing frames in a video stream.

       Initializes the FrameProcessor object with necessary attributes.

       Args:
           cap: The video capture object.
           frame_queue: The queue for storing frames.
           results_queue: The queue for storing processing results.
           queue_event: Event for queue synchronization.
    """

    def __init__(self, cap, frame_queue, results_queue, queue_event, model_name):
        super().__init__()
        self.cap = cap
        self.frame_queue = frame_queue
        self.results_queue = results_queue
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.queue_event = queue_event
        self.frame_buffer = {}
        self.sequence_number = 0
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def run(self):
        """
        Runs the frame processing continuously.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        while self.cap.isOpened():
            if not self.frame_queue.empty():
                frame_high_quality = self.frame_queue.get()
                self.sequence_number += 1
                seq = self.sequence_number
                future = self.executor.submit(self.process_single_frame, frame_high_quality)
                future.add_done_callback(lambda fut: self.processing_done(fut, seq))
            self.check_and_update_queue()
            time.sleep(0.001)

    def processing_done(self, future, sequence):
        """
        Handles the completion of frame processing.

        Args:
            future: The result of the processing task.
            sequence: The sequence number of the frame.

        Returns:
            None
        """
        result, frame = future.result()
        self.frame_buffer[sequence] = (result, frame)

    def check_and_update_queue(self):
        """
        Checks and updates the frame processing queue.
        """
        min_seq = min(self.frame_buffer.keys(), default=None)
        if min_seq is not None:
            self.results_queue.put(self.frame_buffer[min_seq])
            self.queue_event.set()
            del self.frame_buffer[min_seq]

    def process_single_frame(self, frame_high_quality):
        """
        Process a single frame by tracking objects, handling tracking results, and writing frames if recording.

        Args:
            frame_high_quality: The high-quality frame to process.
        """
        model = YOLO(self.model_name).to(self.device)
        return model.track(frame_high_quality, persist=True, verbose=False, device=self.device), frame_high_quality
