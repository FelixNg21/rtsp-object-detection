# Update (Feb 16, 2026)
As Wyze now locks RTSP access behind their subscription service, it is now no longer possible to use [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge)
or any of the forks to expose an RTSP stream for any Wyze cams. This project has come to a close.

# Object Detection on RTSP Stream or Video File

This project aims to re-enable some of the features that Wyze has moved behind their subscription service.
Most notably, the feature that I desired was video recording of unlimited length as long as there was motion or objects 
were detected in frame.

## Description 
This project aims to provide a deployable solution to record video clips when motion is detected in an RTSP stream or a 
video file. Further details can be found in the [`Research`](#research) section.
This project uses a YOLOV11 model provided by [Ultralytics](https://github.com/ultralytics/ultralytics) for object 
detection. 
In order to expose an RTSP stream from my Wyze cameras, I used the [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge)
project. This project is available as a docker container and can be deployed with docker-compose for easy setup on a 
Linux or Windows machine, but not on a Mac due to the lack of GPU access in Docker on Mac. Because of this, I have
created an alternative deployment method for Macs using the Metal Performance Shaders (MPS) framework, with instructions
available [here](#m-series-mac-deployment).


## Deployment

#### Docker Deployment
1. Install [Docker Compose](https://docs.docker.com/compose/install/)
2. Use the `docker-compose-recorder-example.yml` file in the `recorder` folder as a template for your own `docker-compose.yml` file.
3. Run docker-compose up in the directory where the `docker-compose.yml` file is located.

#### M Series Mac Deployment

This branch contains the necessary configuration needed for deployment on an M series Mac, using the Metal Performance 
Shaders (MPS) framework for object detection.

1. Clone the `recorder-mac` branch of the repository.
```bash
git clone -b recorder-mac https://github.com/FelixNg21/rtsp-object-detection.git
```


3. Install the requirements.
```bash
pip install -r requirements.txt
```

4. Install [Docker Compose](https://docs.docker.com/compose/install/)


5. Set up the [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge). I have provided a `docker-compose.yml` file in the repository for easy setup. 
Environment variables can be added and modified according to the [wiki](https://github.com/mrlt8/docker-wyze-bridge/wiki), with details on the
recording settings [here](https://github.com/mrlt8/docker-wyze-bridge/wiki/Stream-Recording-and-Livestreaming).


6. Modify the `config.py` file, mainly the `VIDEO_SOURCE` and `CLIP_DEST` variables. The `VIDEO_SOURCE` variable 
is where the [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge) will save the recorded videos. The `CLIP_DEST` variable is where this program will save the processed clips.


7. (Optional) With a recorded video already saved from [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge).
You can run ```bash python mask_coords.py path/to/video``` and this will open a dialogue box to select the areas of the 
video frame where you do not want to detect objects. The coordinates will be printed to the console and you can copy it
to the `config.py` file under the `MASK_COORDS` variable.


8. Run the program with
```bash
python runner.py
```


## Research
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

# Refactor (`refactor` branch, now merged into `main`)
Code was refactored to be more modular and easier to read. Threading and multiprocessing were also explored to see if
performance could be improved. But it appears that the bottleneck is the inference time of the YOLO model, which I am 
not currently able to improve upon. 

Since this project was meant to be deployable on a low powered device, it looks like I've hit a dead end. I looked into
[Frigate](https://github.com/blakeblackshear/frigate) which is a much more robust and developed solution and the way 
they minimize computational load is to perform motion masks firsts before running object detection. This is likely the
route I will take in the future.

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

# Current work
After my Wyze Cam Plus subscription ended, clip creation have a cooldown and any subsequent motion detection will just 
show the first frame of motion, resulting in no information gained. I've dug around in the 'wyze-bridge' wiki and found
settings that allow for recording of the stream. My current plan is to process the resultant video file and create clips 
if there is motion detected.

A docker-compose-recorder-example.yml is provided in the 'recorder' folder. It outlines the environment variables that
I've used to record the stream.

# Future work
Until I find a suitable device for deployment, I'll look to improving different aspects of the app:

- Adding a front end for video file management/exploration
- Handling multiple RTSP streams (will be hardware dependent)
- Removing the usage of hard-coded variables and move them to environment variables in the docker-compose.yml 