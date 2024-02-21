# rtsp-object-detection

## Introduction

This project started off as a way to return functionality to
Wyze cameras that were slated to have extended video clip recording
locked behind a monthly fee.

My family decided to purchase several Wyze cameras to monitor our home and were enjoying
having clips generated whenever anything was detected in our driveway. These clips used to contain
the entire event, but Wyze decided to limit the length of the clips to 12 seconds unless you paid for Wyze Cam Plus.

I decided to see if I could use this as a learning opportunity to build a system that would allow me to
perform object detection on the video stream and only record the video when motion was detected.

My research started off with following an OpenCV tutorial using YOLO to perform object detection on a video file or
image. The tutorial can be found [here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html).
This can be found in the folder `OpenCV-yolo-tutorial`. It was also adapted to work with an RTSP stream.
I found that this method was fairly slow due to usage of an older version of YOLO and sought other methods.

I then found a tutorial that offloaded the object detection to the AI processes to a local server, which can be found [here](https://www.codeproject.com/Articles/5344693/Object-Detection-with-an-IP-Camera-using-Python-an).
This solution was better than the previous one, but required the local server to be running. 
The resultant video feed was not as smooth as I would have liked and was significantly delayed. This script is in `IP Camera/cam_detection.py`.

There were a myriad of potential reasons behind the delay. One possible reason was that the RTSP stream was not being processed
fast enough. I tried to multithread that process, but `VideoStream` from `imutils` was already multithreaded. I then tried to
use parallelize the object detection process, but that did not seem to help either. This script can be found in `IP Camera/cam_detection_multiprocess.py`.

After further digging, I found a script that ran YOLO locally, bypassing the need for the local server. 
This tutorial can be found [here](https://github.com/akash-agni/Real-Time-Object-Detection/blob/main/Object_Detection_Youtube.py).
I adapted this script to work with an RTSP stream. This script had the best performance which I attribute to the lack of use of a local server.