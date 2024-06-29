import cv2
import time


class VideoCapture:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None

        # Ensure the rtsp stream is up
        while self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.rtsp_url)
            time.sleep(2)

        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

    def get_h(self):
        return self.h

    def get_w(self):
        return self.w

    def get_fps(self):
        return self.fps

    def isOpened(self):
        return self.cap.isOpened()

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()
