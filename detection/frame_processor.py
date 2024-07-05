import threading
from concurrent.futures import ThreadPoolExecutor
import cv2
import time


class FrameProcessor(threading.Thread):
    """
       A class for processing frames in a video stream.

       Initializes the FrameProcessor object with necessary attributes.

       Args:
           cap: The video capture object.
           frame_queue: The queue for storing frames.
           results_queue: The queue for storing processing results.
           process_single_frame: Function to process a single frame.
           queue_event: Event for queue synchronization.

       Returns:
           None
    """

    def __init__(self, cap, frame_queue, results_queue, process_single_frame, queue_event):
        threading.Thread.__init__(self)
        self.cap = cap
        self.frame_queue = frame_queue
        self.results_queue = results_queue
        self.process_single_frame = process_single_frame
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.queue_event = queue_event
        self.frame_buffer = {}
        self.sequence_number = 0
        self.buffer_lock = threading.Lock()

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
            time.sleep(0.1)

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
        with self.buffer_lock:
            self.frame_buffer[sequence] = (result, frame)

    def check_and_update_queue(self):
        """
        Checks and updates the frame processing queue.

        Args:
            None

        Returns:
            None
        """
        with self.buffer_lock:
            keys_to_delete = []
            for seq in sorted(self.frame_buffer.keys()):
                if seq == min(self.frame_buffer.keys()):  # Ensures sequential order
                    self.results_queue.put(self.frame_buffer[seq])
                    self.queue_event.set()
                    keys_to_delete.append(seq)
            for key in keys_to_delete:
                del self.frame_buffer[key]