import os
import queue


class FileManager:
    def __init__(self, path):
        self.path = path
        self.file_queue = queue.Queue()
        self.existing_files = set(self._get_all_files())
        for file in self.existing_files:
            self.file_queue.put(file)

    def _get_all_files(self):
        all_files = set()
        for root, dirs, files in os.walk(self.path):
            for file in files:
                all_files.add(os.path.join(root, file))
        return all_files

    def detect_new_files(self):
        current_files = set(self._get_all_files())
        new_files = current_files - self.existing_files
        for file in new_files:
            self.file_queue.put(file)
        self.existing_files = current_files


    def get_file_queue(self):
        return self.file_queue
