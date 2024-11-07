import os
import queue
import sqlite3


class FileManager:
    def __init__(self, path, db_file='processed_files.db'):
        self.path = path
        self.file_queue = queue.Queue()
        self.db_file = db_file
        self._initialize_db()
        self.existing_files = set(self._get_all_files())
        self.processed_files = self._load_processed_files()
        for file in self.existing_files - self.processed_files:
            self.file_queue.put(file)

    def _initialize_db(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_files (
                id INTEGER PRIMARY KEY,
                file_path TEXT UNIQUE
            )
        ''')
        self.conn.commit()

    def _get_all_files(self):
        all_files = set()
        for root, dirs, files in os.walk(self.path):
            for file in files:
                all_files.add(os.path.join(root, file))
        return all_files

    def _load_processed_files(self):
        self.cursor.execute('SELECT file_path FROM processed_files')
        return set([row[0] for row in self.cursor.fetchall()])

    def _save_processed_file(self, file):
        self.cursor.execute('INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)', (file,))
        self.conn.commit()

    def detect_new_files(self):
        current_files = set(self._get_all_files())
        new_files = current_files - self.existing_files
        for file in new_files:
            if file not in self.processed_files:
                self.file_queue.put(file)
        self.existing_files = current_files

    def get_file_queue(self):
        return self.file_queue

    def mark_file_as_processed(self, file):
        self.processed_files.add(file)
        self._save_processed_file(file)

