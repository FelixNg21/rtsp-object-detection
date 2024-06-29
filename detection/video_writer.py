import datetime
import os
import zoneinfo
import cv2


class VideoWriter:
    def __init__(self, video_dir, w, h, fps):
        self.video_dir = video_dir
        self.w = w
        self.h = h
        self.fps = fps

        self.video_writer = None
        self.recording = False

    def start_recording(self):
        """
        Initialize the video writer to start recording a video.
        """
        if not self.video_writer:
            self.recording = True
            now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Vancouver"))
            now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
            dir_structure = now.strftime("%Y/%m/%d")
            dirname = f"{self.video_dir}/{dir_structure}"
            filename = f"{dirname}/{now_str}.mp4"

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.video_writer = cv2.VideoWriter(
                filename,
                cv2.VideoWriter_fourcc(*'mp4v'),
                self.fps,
                (self.w, self.h),
            )
            print("Created video_writer")

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
        self.video_writer.release()
        self.video_writer = None
        self.recording = False

    def cleanup(self):
        """
        Cleanup the video writer.
        """
        if self.video_writer is not None:
            self.video_writer.release()
