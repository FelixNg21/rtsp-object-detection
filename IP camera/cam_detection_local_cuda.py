# This is an attempt to run without CodeProject AI, by running YoloV5 locally.
# Adapted from https://github.com/akash-agni/Real-Time-Object-Detection/blob/main/Object_Detection_Youtube.py
# An issue that was found was that multiple bounding boxes were drawn for the same object in the same frame,
# when running on cuda. This was not seen when running on cpu.
# This thread: https://github.com/ultralytics/yolov3/issues/1188, while addressing the same issue on yolov3, provided
# insight into the issue. The issue is most likely due to the fact that the stream is being read from a VideoStream,
# which is multi-threaded. This leads to a scenario where the bounding boxes are drawn on the same frame multiple times.
# By sending a copy of the frame to the plot_to_boxes method, the issue is resolved.

import imutils
import torch
from imutils.video import VideoStream
import cv2



class ObjectDetection:
    """
    Class implements Yolo5 model to make inferences on a rtsp videostream using Opencv2.
    """

    def __init__(self, rstp_link):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        self._rtsp_link = rstp_link
        self.model = self.load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def get_stream_from_url(self):
        """
        Creates a new video streaming object to extract video frame by frame to make prediction on.
        :return: opencv2 video capture object, with lowest quality frame available for video.
        """
        return VideoStream(self._rtsp_link)

    def load_model(self):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Trained Pytorch model.
        """
        model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)
        model.conf = 0.45
        return model

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:, :-1].cpu().numpy()
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
            bgr = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
            cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)

        return frame

    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        vs = self.get_stream_from_url().start()
        while True:
            frame = vs.read()
            if frame is None:
                continue
            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame.copy())
            frame = imutils.resize(frame, width=1080)
            cv2.imshow("WyzeCam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        vs.stop()

if __name__ == "__main__":
    # Create a new object and execute.
    a = ObjectDetection("rtsp://localhost:8554/driveway")
    a()