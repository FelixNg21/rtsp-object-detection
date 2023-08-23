# Detects objects in a video stream from an IP camera
# An attempt to use threading to improve performance was attempted but was not successful as VideoStream is already
# threaded, so the bottleneck would be in the do_detection method.
# Source: https://www.codeproject.com/Articles/5344693/Object-Detection-with-an-IP-Camera-using-Python-an

import cv2
import imutils
from imutils.video import VideoStream
import io
import requests
import numpy as np
from PIL import Image, ImageDraw

rtsp_url = "rtsp://localhost:8554/driveway"


def do_detection(image, session):
    '''
    Detects objects in the image using CodeProject AI
    :param image: image object to detect
    :param session: session object to use for the request
    :return: image object with bounding boxes drawn
    '''
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)

    response = session.post("http://localhost:32168/v1/vision/detection/",
                            files={"image": ('image.png', buf, 'image/png')},
                            data={"min_confidence": 0.5}).json()

    predictions = response["predictions"]
    if predictions is None:
        predictions = []

    draw = ImageDraw.Draw(image)
    for object_detected in predictions:
        label = object_detected["label"]
        conf = object_detected["confidence"]
        y_max = int(object_detected["y_max"])
        y_min = int(object_detected["y_min"])
        x_max = int(object_detected["x_max"])
        x_min = int(object_detected["x_min"])

        draw.rectangle([(x_min, y_min), (x_max, y_max)], outline="red", width=5)
        draw.text((x_min, y_min), f"{label}")
        draw.text((x_min, y_min - 10), f"{round(conf * 100.0, 0)}")

    return image


def main():
    # Open the RTSP stream
    vs = VideoStream(rtsp_url, framerate=120).start()
    session = requests.Session()

    while True:

        frame = vs.read()
        if frame is None:
            continue

        image = Image.fromarray(frame)
        image = do_detection(image, session)
        frame = np.asarray(image)

        frame = imutils.resize(frame, width=1080)
        cv2.imshow('WyzeCam', frame)

        # Wait for the user to hit 'q' for quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    session.close()
    vs.stop()


if __name__ == "__main__":
    main()
