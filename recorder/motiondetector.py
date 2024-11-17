from ultralytics import YOLO
import cv2
import torch
from collections import defaultdict
import numpy as np
import time
import signal


class MotionDetector:
    def __init__(self, model_name, movement_threshold, delay_time, video_writer, mask_coords=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO(model_name).to(self.device)
        self.movement_threshold = movement_threshold
        self.delay_time = delay_time
        self.video_writer = video_writer
        self.track_history = defaultdict(lambda: [])
        self.motion_stop_time = None

        # Load mask coordinates
        self.mask = None
        if mask_coords:
            self.mask = np.zeros((1080, 1920), dtype=np.uint8)
            cv2.fillPoly(self.mask, [np.array(mask_coords)], 255)
            self.mask = cv2.bitwise_not(self.mask)

        # Register signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def run(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if self.mask is not None:
                frame_masked = cv2.bitwise_and(frame, frame, mask=self.mask)
                results = self.model.track(frame_masked, persist=True, verbose=False)
            else:
                results = self.model.track(frame, persist=True, verbose=False)
            self.handle_tracking(results, filename=video_path)
            if self.video_writer.recording:
                print("Writing frame")
                self.video_writer.write_frame(frame)
        cap.release()
        self.video_writer.cleanup()

    def handle_tracking(self, results, filename=None):
        boxes = results[0].boxes.xywh.cpu()
        if results[0].boxes.id is not None:
            boxes_cpu = results[0].boxes.cpu()
            clss = boxes_cpu.cls.tolist()  # can filter unwanted classes
            names = results[0].names # all class names in model
            track_ids = boxes_cpu.id.int().tolist()
            for box, cls, track_id in zip(boxes, clss, track_ids):
                self.track_history[track_id].append((box[0], box[1]))
                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track_id, filename)

    def plot_tracks(self, track_id, filename):
        prev_center = np.array(self.track_history[track_id][-2])
        curr_center = np.array(self.track_history[track_id][-1])
        displacement = np.linalg.norm(curr_center - prev_center)

        if displacement >= self.movement_threshold:
            if not self.video_writer.recording:
                self.video_writer.start_recording(filename)
            self.motion_stop_time = None
        else:
            if self.motion_stop_time is None:
                self.motion_stop_time = time.time()
            if self.video_writer.recording and (time.time() - self.motion_stop_time) > self.delay_time:
                self.video_writer.stop_recording()
                self.track_history.clear()
                self.motion_stop_time = None

    def signal_handler(self, signum, frame):
        if self.video_writer.recording:
            self.video_writer.stop_recording()
        self.video_writer.cleanup()
