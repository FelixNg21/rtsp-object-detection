import os
import time


class FileManager:
    def __init__(self, video_directory, days_threshold):
        # Directory where the video files are stored
        self.video_dir = video_directory
        self.days_threshold = days_threshold

    def cleanup_files(self):
        total_size = 0
        files_to_delete = []

        # Calculate total size and identify files to delete based on days threshold
        for file in os.listdir(self.video_dir):
            file_path = os.path.join(self.video_dir, file)
            file_creation_time = os.path.getctime(file_path)
            if time.time() - file_creation_time > self.days_threshold * 24 * 3600:
                files_to_delete.append(file)
            total_size += os.path.getsize(file_path)

        # Delete files based on space threshold if total size exceeds the threshold
        while files_to_delete:
            file = files_to_delete.pop(0)
            file_path = os.path.join(self.video_dir, file)
            total_size -= os.path.getsize(file_path)
            os.remove(file_path)
            print(f"Deleted: {file}")

        print("Cleanup completed.")
