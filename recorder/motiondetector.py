from ultralytics import YOLO
import cv2
import torch
from collections import defaultdict
import numpy as np
import time

class MotionDetector:
    def __init__(self, model_name, movement_threshold, delay_time, video_writer):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO(model_name).to(self.device)
        self.movement_threshold = movement_threshold
        self.delay_time = delay_time
        self.video_writer = video_writer
        self.track_history = defaultdict(lambda: [])
        self.motion_stop_time = None

    def run(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results = self.model.track(frame, persist=True, verbose=False)
            self.handle_tracking(results)
            if self.video_writer.recording:
                self.video_writer.write_frame(frame)
        cap.release()
        self.video_writer.stop_recording()

    def handle_tracking(self, results):
        boxes = results[0].boxes.xywh.cpu()
        if results[0].boxes.id is not None:
            boxes_cpu = results[0].boxes.cpu()
            clss = boxes_cpu.cls.tolist() # can filter unwanted classes
            track_ids = boxes_cpu.id.int().tolist()
            for box, cls, track_id in zip(boxes, clss, track_ids):
                self.track_history[track_id].append((box[0], box[1]))
                if len(self.track_history[track_id]) >= 2:
                    self.plot_tracks(track_id)

    def plot_tracks(self, track_id):
        prev_center = np.array(self.track_history[track_id][-2])
        curr_center = np.array(self.track_history[track_id][-1])
        displacement = np.linalg.norm(curr_center - prev_center)

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


from detection.video_writer import VideoWriter

vw = VideoWriter("C:\\Users\Felix\Desktop\Camera\clips", 1920, 1080, 20)
md = MotionDetector("yolo11n.pt", 15, 5, vw)
md.run("C:\\Users\Felix\Desktop\Camera\\videos\driveway\\2024-11-04\driveway_14_04_52.mp4")
cv2.destroyAllWindows()