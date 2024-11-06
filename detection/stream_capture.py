import cv2


class StreamCapture:
    """
    A class for capturing video from an RTSP stream.

    Initializes the StreamCapture object with the RTSP URL and captures video frames.

    Args:
        rtsp_url: The RTSP URL for the video stream.
    """

    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None

        while self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if not self.cap.isOpened():
                print("Error opening video stream or file")

        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

    def get_h(self):
        """
        Returns the height of the captured video frames.
        """
        return self.h

    def get_w(self):
        """
        Returns the width of the captured video frames.
        """
        return self.w

    def get_fps(self):
        """
        Returns the frames per second of the captured video.
        """
        return self.fps

    def isOpened(self):
        """
        Checks if the video capture is open. Returns True if open, False otherwise.
        """
        return self.cap.isOpened()

    def read(self):
        """
        Reads the next video frame.

        Returns:
            A tuple containing a boolean indicating success and the frame.
        """
        return self.cap.read()

    def release(self):
        """
        Releases the video capture resources.
        """
        self.cap.release()
