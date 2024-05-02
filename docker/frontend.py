from nicegui import app, ui
from pathlib import Path
from typing import Optional
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

class FileChangeHandler(LoggingEventHandler):
    def __init__(self, file_explorer):
        super().__init__()
        self.file_explorer = file_explorer

    def on_modified(self, event):
        self.file_explorer.display_grid()

class FileExplorer:
    def __init__(self, directory: str):
        self.path = Path(directory)
        self.base_dir = Path(directory)
        self.selected_file = None
        self.selected_folder = None
        self.grid=ui.grid()
        self.display_grid()

        # Watch for changes in the directory
        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()

    def display_grid(self, path: Optional[Path] = None):
        selected_path = path or self.path
        self.grid.clear()
        with self.grid:
            ui.button("...", on_click=self.go_up, icon='folder')
            for file in selected_path.iterdir():
                if file.is_dir():
                    ui.button(file.name, on_click=lambda event: self.select_folder(file.name), icon='folder')
                elif file.is_file():
                    ui.button(file.name, on_click=lambda event: self.select_file(file.name), icon='file')


    def select_file(self, file_name):
        self.selected_file = file_name
        self.selected_folder = None

        ui.notify(f'You chose {self.selected_file}')

    def select_folder(self, folder_name):
        self.selected_folder = folder_name
        self.selected_file = None
        path = str(Path(self.path))
        ui.notify(f'You chose {self.selected_folder}')

        self.display_grid(path/Path(self.selected_folder))

    def go_up(self):
        if self.path.parent != self.path and self.base_dir in self.path.parents:
            self.path = self.path.parent
            self.display_grid()

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
    directory = 'C:\\Users\Felix\Desktop\Camera\\videos'
    FileExplorer(directory)
    ui.run()

