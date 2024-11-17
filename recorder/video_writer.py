import datetime
import os
import zoneinfo
import cv2


class VideoWriter:
    """
    A class for writing video frames to a video file.

    Initializes the VideoWriter object with the video directory, width, height, and frames per second.

    Args:
        video_dir: The directory to save the video file.
        w: The width of the video frames.
        h: The height of the video frames.
        fps: The frames per second of the video.

    Returns:
        None
    """
    def __init__(self, video_dir, w, h, fps):
        self.video_dir = video_dir
        self.w = w
        self.h = h
        self.fps = fps

        self.video_writer = None
        self.recording = False

    def start_recording(self, filename):
        """
        Initialize the video writer to start recording a video.
        """
        if not self.video_writer:
            self.recording = True
            date = filename.split("/")[2]
            time_h = filename.split("/")[3].split("_")[1]
            time_s = filename.split("/")[3].split("_")[2]
            time_ms = filename.split("/")[3].split("_")[3].split(".")[0]
            filename_dest = f"{self.video_dir}/{date}/{date}_{time_h}_{time_s}_{time_ms}.mp4"
            # filename = self._generate_filename()
            # print(f"filename:", filename)
            self._create_directory(filename_dest)
            self.video_writer = cv2.VideoWriter(
                filename_dest,
                cv2.VideoWriter_fourcc(*'mp4v'),
                self.fps,
                (self.w, self.h),
            )
            print("Created video_writer")

    def _generate_filename(self):
        """
        Generate a filename based on the current date and time.
        """
        now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Vancouver"))
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        dir_structure = now.strftime("%Y/%m/%d")
        return f"{self.video_dir}/{dir_structure}/{now_str}.mp4"

    def _create_directory(self, filename):
        """
        Create the directory structure for the given filename.
        """
        directory = os.path.dirname(filename)
        os.makedirs(directory, exist_ok=True)

    def write_frame(self, frame):
        """
        Write a frame to the video.

        Args:
            frame (np.array): A frame to write to the video.
        """
        self.video_writer.write(frame)

    def stop_recording(self):
        """
        Stop recording a video.
        """
        if self.video_writer is not None:
            self.video_writer.release()
        self.video_writer = None
        self.recording = False
        print("Stopped recording")

    def cleanup(self):
        """
        Cleanup the video writer.
        """
        if self.video_writer is not None:
            self.video_writer.release()
