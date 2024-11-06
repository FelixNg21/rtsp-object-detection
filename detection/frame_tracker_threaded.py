import queue
import threading
import time
import numpy as np


class FrameTracker(threading.Thread):
    """
    A class for tracking frames and objects in a video stream.

    Initializes the FrameTracker object with necessary attributes.

    Args:
        results_queue: The queue for storing detection results.
        video_writer: The video writer object.
        track_movement_history: Function to track movement history.
        write_frame: Function to write frames.
        track_history: Dictionary to store object tracking history.
        queue_event: Event for queue synchronization.
    """

    def __init__(self, results_queue, video_writer, track_movement_history, write_frame,
                 track_history, queue_event, motion_stop_time, delay_time, movement_threshold):
        super().__init__()

        self.results_queue = results_queue
        self.video_writer = video_writer
        self.track_movement_history = track_movement_history
        self.write_frame = write_frame
        self.track_history = track_history
        self.queue_event = queue_event
        self.motion_stop_time = motion_stop_time
        self.delay_time = delay_time
        self.movement_threshold = movement_threshold

    def run(self):
        """
        Runs the frame tracking process continuously.
        """

        while True:
            self.queue_event.wait()
            items = []
            while not self.results_queue.empty():
                try:
                    items.append(self.results_queue.get_nowait())
                    # results, frame = self.results_queue.get_nowait()
                except queue.Empty:
                    break
            for results, frame in items:
                self.handle_tracking(results)
                if self.video_writer.recording:
                    self.write_frame(frame)

            time.sleep(0.1)
            self.queue_event.clear()

    def handle_tracking(self, results):
        """
        Handles the tracking of objects based on detection results.

        Args:
            results: The detection results to process.
        """

        boxes = results[0].boxes.xyxy.cpu()
        if results[0].boxes.id is not None:
            boxes_cpu = results[0].boxes.cpu()
            clss = boxes_cpu.cls.tolist()
            track_ids = boxes_cpu.id.int().tolist()

            for box, cls, track_id in zip(boxes, clss, track_ids):
                self.track_movement_history(track_id, box)
                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track_id)

    def plot_tracks(self, track_id):
        """
        Calculate displacement between previous and current track centers,
        start or stop recording based on movement threshold and recording status.

        Args:
            track_id: The identifier of the track to process.
        """
        prev_center = np.array(self.track_history[track_id][-2])
        current_center = np.array(self.track_history[track_id][-1])
        displacement = np.linalg.norm(prev_center - current_center)

        # Plot tracks if sufficient movement
        if displacement >= self.movement_threshold:
            if not self.video_writer.recording:
                self.video_writer.start_recording()
            self.motion_stop_time = None

        else:
            if self.motion_stop_time is None:
                self.motion_stop_time = time.time()
            if self.video_writer.recording and (time.time() - self.motion_stop_time) > self.delay_time:
                self.video_writer.stop_recording()
                self.track_history.clear()
                self.motion_stop_time = None
