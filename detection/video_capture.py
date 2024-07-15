import cv2


class VideoCapture:
    """
    A class for capturing video from an RTSP stream.

    Initializes the VideoCapture object with the RTSP URL and captures video frames.

    Args:
        rtsp_url: The RTSP URL for the video stream.

    Returns:
        None
    """

    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(self.rtsp_url)

        # Ensure the rtsp stream is up
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open RTSP stream: {self.rtsp_url}")

        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

    def get_h(self):
        """
        Returns the height of the captured video frames.

        Args:
            None

        Returns:
            The height of the video frames.
        """
        return self.h

    def get_w(self):
        """
        Returns the width of the captured video frames.

        Args:
            None

        Returns:
            The width of the video frames.
        """
        return self.w

    def get_fps(self):
        """
        Returns the frames per second of the captured video.

        Args:
            None

        Returns:
            The frames per second of the video.
        """
        return self.fps

    def isOpened(self):
        """
        Checks if the video capture is open.

        Args:
            None

        Returns:
            True if the video capture is open, False otherwise.
        """
        return self.cap.isOpened()

    def read(self):
        """
        Reads the next video frame.

        Args:
            None

        Returns:
            A tuple containing a boolean indicating success and the frame.
        """
        return self.cap.read()

    def release(self):
        """
        Releases the video capture resources.

        Args:
            None

        Returns:
            None
        """
        self.cap.release()
