from filemanager import FileManager
from processor import VideoProcessor
import os
import time

if __name__ == "__main__":
    video_path = "C:\\Users\Felix\Desktop\Camera\\videos"

    file_manager = FileManager(video_path)

    while True:
        file_manager.detect_new_files()

        file_queue = file_manager.get_file_queue()
        while not file_queue.empty():
            video_file = file_queue.get()
            print(f"Processing {video_file}")
            video_processor = VideoProcessor(os.path.join(video_path, video_file))
            video_processor.process()
            video_processor.release_clip_writer()
        time.sleep(60)
