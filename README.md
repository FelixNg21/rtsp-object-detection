# RTSP Object Detection

## Background
This project aims to re-enable some of the features that Wyze has moved behind their subscription service.
Most notably, the feature that I desired was video recording of unlimited length as long as there was motion or objects 
were detected in frame.
Several events in my neighbourhood has prompted me to begin working on this project, where I was requested to provide 
footage that my Wyze cameras have recorded around the property.
Because only one camera was set to continuously record and the rest only recorded when there was a detection, I only had 
just 7 (12 if subscribed to Wyze Cam Plus) seconds of video clips unless I manually used the app to create video clips 
from the camera that was continuously recording.
Wyze's app UI is extremely cumbersome and makes it extremely difficult to scrub to a specific time in order to create a 
clip of recorded footage.

# Research (`dev` branch)
This project began by exploring existing projects, which led me to this tutorial 
[here](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html). 
This project used a YOLO model to perform object detection on a video file or image and was subsequently adapted to work
with an RTSP stream.
My exploration can be found in `OpenCV-yolo-tutorial`.
Unfortunately, I found that the process was fairly slow due to the usage of an older YOLO model and went to look for 
better methods.

I then found a tutorial that offloaded the object detection to a local server, which can be found 
 [here](https://www.codeproject.com/Articles/5344693/Object-Detection-with-an-IP-Camera-using-Python-an).
This solution was better than the previous one, but the recorded video was quite choppy and was significantly delayed.
Work can be find in `IP camera/cam_detection.py`.

There were a myriad of potential reasons behind the delay. One possible reason was that the RTSP stream was not being processed
fast enough. I tried to multithread that process, but `VideoStream` from `imutils` was already multithreaded. I then tried to
use parallelize the object detection process, but that did not seem to help either. This script can be found in `IP Camera/cam_detection_multiprocess.py`.

After further digging, I found a script that ran YOLO locally, bypassing the need for the local server. 
This tutorial can be found [here](https://github.com/akash-agni/Real-Time-Object-Detection/blob/main/Object_Detection_Youtube.py).
I adapted this script to work with an RTSP stream. This script had the best performance which I attribute to the lack of use of a local server.

# Working model
This brings me to the latest iteration of the project, which heavily depends on another GitHub 
[repo](https://github.com/mrlt8/docker-wyze-bridge) that provides a nice UI to browse a feed from all my Wyze cameras,
as well as provide an RTSP stream url.

Since the `wyze-bridge` can be deployed via docker compose, that was the direction I looked to make my solution simplest
to use. An example docker compose file can be found in `detection/docker-compose-example.yml`.
My program uses a YOLOv8 model provided by [Ultralytics](https://github.com/ultralytics/ultralytics), which means that 
the inference time on a relatively new machine is very quick, emphasis on relatively new machine. 
It works reliably and quickly on a machine with an Intel i7-13700k as well as a MacBook with an M1 Pro, but I did not 
want to deploy on my personal rig nor my laptop, so I looked to the laptop I used during uni.

# Attempted Deployment
This device has an anemic and already underpowered CPU for its time, an Intel M3-6y30. I found that inference time 
would be pushing one minute and serve to be unusable as a deployment device. 

I explored multiprocessing to offload different tasks to different cores, but since the inference time was the bottleneck,
the only real solution that I think I have would be to build some sort of home server or find a second hand device 
for cheap. 
I also tried to use a sub-stream for the RTSP stream provided by the `wyze-bridge`, hoping that inference on a lower
resolution video frame would be accelerated, but the stream is delayed by several seconds, resulting in the bounding box
being ahead of the object when added to the full resolution stream.

# Future work
Until I find a suitable device for deployment, I'll look to improving different aspects of the app:

- Adding a front end for video file management/exploration
- Handling multiple RTSP streams (will be hardware dependent)
- Removing the usage of hard-coded variables and move them to environment variables in the docker-compose.yml 

