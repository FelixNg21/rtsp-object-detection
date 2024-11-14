from filemanager import FileManager
from video_writer import VideoWriter
from motiondetector import MotionDetector
import config
import time

if __name__ == "__main__":
    video_path = "C:\\Users\Felix\Desktop\Camera\\videos"
    file_manager = FileManager(video_path)

    video_dir = "C:\\Users\Felix\Desktop\Camera\clips"
    model_name = config.MODEL_NAME
    movement_threshold = config.MOVEMENT_THRESHOLD
    delay_time = config.DELAY_TIME

    video_writer = VideoWriter(video_dir, 1920, 1080, 20)

    mask_coords = config.MASK_COORDS
    motion_detector = MotionDetector(model_name, movement_threshold, delay_time, video_writer, mask_coords)
    while True:
        file_manager.detect_new_files()

        file_queue = file_manager.get_file_queue()
        while not file_queue.empty():
            video_file = file_queue.get()
            file_manager.mark_file_as_processed(video_file)
            motion_detector.run(video_file)

        time.sleep(60)
