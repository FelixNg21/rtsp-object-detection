import threading
import time


class FrameTracker(threading.Thread):
    def __init__(self, cap, results_queue, video_writer, track_movement_history, plot_tracks, write_frame,
                 track_history, queue_event):
        threading.Thread.__init__(self)
        self.cap = cap
        self.results_queue = results_queue
        self.video_writer = video_writer
        self.track_movement_history = track_movement_history
        self.plot_tracks = plot_tracks
        self.write_frame = write_frame
        self.track_history = track_history
        self.queue_event = queue_event


    def run(self):
        """
        Runs the frame tracking process continuously.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        while True:
            self.queue_event.wait()
            while not self.results_queue.empty():
                results, frame = self.results_queue.get()
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

        Returns:
            None
        """

        boxes = results[0].boxes.xyxy.cpu()
        if results[0].boxes.id is not None:
            clss = results[0].boxes.cls.cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, cls, track_id in zip(boxes, clss, track_ids):
                self.track_movement_history(track_id, box)
                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track_id)
