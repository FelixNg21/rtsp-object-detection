from nicegui import app, ui
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

import requests


class FileChangeHandler(LoggingEventHandler):
    def __init__(self, file_explorer):
        super().__init__()
        self.file_explorer = file_explorer

    def on_modified(self, event):
        self.file_explorer.display_container()


class FileExplorer:
    def __init__(self, directory: str):
        self.path = Path(directory)
        self.base_dir = Path(directory)
        self.selected_file = None
        self.selected_folder = None
        self.prev_dir = None

        self.media = Path('media')
        self.media.mkdir(exist_ok=True)

        self.video_container = None
        self.display_container()

        # Watch for changes in the directory
        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, directory, recursive=True)
        self.observer.start()

    def display_container(self, path: Optional[Path] = None):
        selected_path = path or self.path

        ui.label(f"Selected path: {selected_path}")
        if self.video_container:
            self.video_container.clear()
        self.video_container = ui.row().classes("full flex")
        with self.video_container:
            ui.button("...", on_click=self.go_up, icon='folder')
            for file in selected_path.iterdir():
                if file.is_dir():
                    ui.button(file.name, on_click=lambda: self.select_folder(file.name), icon='folder')
                elif file.is_file():
                    (self.media/file.name).write_bytes(file.read_bytes())
                    app.add_media_file(url_path="/media/", local_file=self.media/file.name)
                    ui.video(f"./media/{file.name}")

    def select_file(self, file_name):
        self.selected_file = file_name
        self.selected_folder = None

        ui.notify(f'You chose {self.selected_file}')

    def select_folder(self, folder_name):
        self.prev_dir = self.path
        self.path = self.path / Path(folder_name)

        self.selected_folder = folder_name
        self.selected_file = None
        ui.notify(f'You chose {self.selected_folder}')

        self.display_container(self.path)

    def go_up(self):
        if self.path.parent != self.path and self.base_dir in self.path.parents:
            self.prev_dir = self.path
            self.path = self.path.parent
            self.display_container(self.path)

    def select(self):
        if self.selected_file:
            ui.notify(f'You chose {self.selected_file}')
        elif self.selected_folder:
            ui.notify(f'You chose {self.selected_folder}')
        else:
            ui.notify('Please select a file or folder')

    def stop(self):
        self.observer.stop()
        self.observer.join()


if __name__ in {"__main__", "__mp_main__"}:
    directory = ('C:\\Users\Felix\Desktop\Camera\\rtsp-object-detection\docker\\videos')
    FileExplorer(directory)
    ui.run()
