import cv2
import os
from ultralytics import YOLO


class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.clip_writer = None
        self.clip_path = None
        self.model = YOLO('yolov8n.pt')
        self.detected_objects = set()

    def process(self):
        cap = cv2.VideoCapture(self.video_path)
        ret, frame = cap.read()

        while cap.isOpened():
            if not ret:
                break

            results = self.model(frame)  # Perform object detection
            new_objects = set()

            for result in results:
                for obj in result.boxes:
                    label = obj.cls
                    new_objects.add(label)

            if new_objects - self.detected_objects:
                self.save_clip(frame)
                self.detected_objects.update(new_objects)

            ret, frame = cap.read()

        cap.release()
        self.release_clip_writer()
        cv2.destroyAllWindows()

    def save_clip(self, frame):
        if self.clip_writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.clip_path = os.path.join(os.path.dirname(self.video_path), 'motion_clip.avi')
            self.clip_writer = cv2.VideoWriter(self.clip_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))

        self.clip_writer.write(frame)

    def release_clip_writer(self):
        if self.clip_writer is not None:
            self.clip_writer.release()
            self.clip_writer = None
