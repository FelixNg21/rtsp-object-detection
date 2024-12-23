from filemanager import FileManager
from video_writer import VideoWriter
from motiondetector import MotionDetector
import config

import datetime

if __name__ == "__main__":
    video_path = config.VIDEO_SOURCE
    file_manager = FileManager(video_path)

    video_dir = config.CLIP_DEST
    video_writer = VideoWriter(video_dir, 1920, 1080, 20)

    model_name = config.MODEL_NAME
    movement_threshold = config.MOVEMENT_THRESHOLD
    delay_time = config.DELAY_TIME
    mask_coords = config.MASK_COORDS
    motion_detector = MotionDetector(model_name, movement_threshold, delay_time, video_writer, mask_coords)
    while True:
        file_manager.detect_new_files()
        file_queue = file_manager.get_file_queue()

        while not file_queue.empty():
            video_file = file_queue.get()
            print(f"{datetime.datetime.now().time()} Processing file: ", video_file)
            file_manager.mark_file_as_processed(video_file)
            motion_detector.run(video_file)

