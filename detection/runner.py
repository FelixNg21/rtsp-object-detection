from video_writer import VideoWriter
from motion_detector_threaded import MotionDetector
from file_manager import FileManager
from video_capture import VideoCapture
import config
import time


if __name__ == "__main__":
    # Create Video Capture object
    # url = config.RTSP_URL + config.RTSP_CAM_NAME[0]
    url = "rtsp://localhost:8554/driveway"

    print("Starting")
    cap = VideoCapture(url)
    print("Started video capture")

    # Create Video Writer object
    video_dir = config.VIDEO_DIR
    h = cap.get_h()
    w = cap.get_w()
    fps = cap.get_fps()
    video_writer = VideoWriter(video_dir, w, h, fps)

    # Create File Manager object
    day_threshold = config.DAY_THRESHOLD
    file_manager = FileManager(video_dir, day_threshold)

    # Create Motion Detector object
    model_name = config.MODEL_NAME
    movement_threshold = config.MOVEMENT_THRESHOLD
    delay_time = config.DELAY_TIME
    motion_detector = MotionDetector(cap, movement_threshold, delay_time, video_writer, model_name)

    # Start
    motion_detector.run()
