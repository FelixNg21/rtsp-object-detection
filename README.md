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
image.
This can be found in the folder `OpenCV-yolo-tutorial`.