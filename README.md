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

