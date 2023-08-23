# Detects objects in a video stream from an IP camera
# An attempt to use threading to improve performance was attempted but was not successful as VideoStream is already
# threaded, so the bottleneck would be in the do_detection method.

# Here an attempt at multiprocessing is made. The idea is to have the do_detection method run in a pool.
# Source: https://www.codeproject.com/Articles/5344693/Object-Detection-with-an-IP-Camera-using-Python-an

import argparse
import cv2
import imutils
from imutils.video import VideoStream, FPS
import io
import requests
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool, Queue

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

    # return image
    detection_buffer.put(np.asarray(image))


def init_pool(d_buffer):
    global detection_buffer
    detection_buffer = d_buffer


def show():
    while args["display"] > 0:
        frame = detection_buffer.get()
        if frame is not None:
            frame = imutils.resize(frame, width=1080)
            cv2.imshow("WyzeCam", frame)
        else:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return


ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=200,
                help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")
args = vars(ap.parse_args())


def main():
    # Open the RTSP stream
    vs = VideoStream(rtsp_url).start()
    session = requests.Session()
    fps = FPS().start()

    detection_buffer = Queue()
    pool = Pool(19, init_pool, (detection_buffer,))
    show_future = pool.apply_async(show)
    futures = []

    # while True:
    while fps._numFrames < args["num_frames"]:
        frame = vs.read()
        if frame is None:
            continue

        image = Image.fromarray(frame)
        f = pool.apply_async(do_detection, args=(image, session))
        futures.append(f)

        fps.update()

    for f in futures:
        f.get()
    detection_buffer.put(None)
    show_future.get()

    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    cv2.destroyAllWindows()
    session.close()
    vs.stop()


if __name__ == "__main__":
    main()
