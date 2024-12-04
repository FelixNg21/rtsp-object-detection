# Near Real Time RTSP Object Detection

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



# M Series Mac Deployment
This branch contains the necessary configuration needed for deployment on an M series Mac, using the Metal Performance 
Shaders (MPS) framework for object detection.

## Usage
1. Clone the repository
```bash
git clone -b recorder-mac https://github.com/FelixNg21/rtsp-object-detection.git
```

2. Verify that Python 3.11 is installed with
```bash
python --version
```


3. Create a new virtual environment.
```bash
cd recorder
python -m venv venv
source venv/bin/activate
```


4. Install the requirements.
```bash
pip install -r requirements.txt
```

5. Install Docker.


6. Set up the [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge). Docker compose is recommended for 
setup. I have provided a `docker-compose.yml` file in the repository for easy setup. Environment variables can be 
added and modified according to the [wiki](https://github.com/mrlt8/docker-wyze-bridge/wiki), with details on the
recording settings [here](https://github.com/mrlt8/docker-wyze-bridge/wiki/Stream-Recording-and-Livestreaming).


7. Modify the `config.py` file, mainly the `VIDEO_SOURCE` and `CLIP_DEST` variables. The `VIDEO_SOURCE` variable 
is where the [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge) will save the recorded videos. The 
`CLIP_DEST` variable is where this program will save the processed clips.


8. (Optional) With a recorded video already saved from [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge).
You can run ```bash python mask_coords.py path/to/video``` and this will open a dialogue box to select the areas of the 
video frame where you do not want to detect objects. The coordinates will be printed to the console and you can copy it
to the `config.py` file under the `MASK_COORDS` variable.


9. Run the program with
```bash
python runner.py
```

## Context
I originally intended to use my original Docker container for deployment along with 
[docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge). However, Docker on Mac does not have access to the 
Mac's GPU, rendering the container useless for this project. I have made modifications to my script to run on my M1
Macbook Pro with Metal Performance Shaders (MPS) and they are sufficient for the project to run. 

The [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge) is currently set up to record in 60 second
intervals and the M1 chip is able to process each new video clip in under 60 seconds, meaning that the project is able
to run in near real time. I will explore longer clips segments in the future, but as I'm trying to keep the project as
close to real time as possible, keeping the segments at 60 seconds is the best option.

