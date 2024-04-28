# rtsp-object-detection

This project aims to re-enable some of the free features that Wyze has moved behind a subscription service. 
Wyze used to enable video clips of unlimited lengths for as long as there was motion and/or objects detected, as of the time of writing, this feature is now behind a subscription service and clips can only be 12 seconds.
Several recent events in my neighbourhood have prompted me to look into this project, where I was requested to provide any available footage. 
Unfortunately, Wyze's current implementation does allow for continuous recording, but the 12 seconds clips are not enough to capture the full event. 
The user interface to record and download the clips are very unintuitive and cumbersome to use, but that will be a separate feature to implement.

The program uses opencv and yolov8 to detect motion in an RTSP stream and create video clips.

This branch is a "deployable" version that depends on another GitHub [repository](https://github.com/mrlt8/docker-wyze-bridge) to provide the RTSP stream.
A docker-compose.yml file is provided to run the program, but hard-coded values are in the Python file so it will not be able to run without modification.

# Attempted Deployment
As my old laptop (ASUS UX305CA - Intel m3-6y30) is not powerful enough to run the YOLO inference quickly enough, large developments will slow down until I figure out some sort of home lab setup.

# Experiments
- Attempted to use a substream provided by the docker-wyze-bridge, but it was out of sync with the main stream. This resulted in the bounding boxes being off by several seconds. I had thought that tracking based on a lower resolution image would be less intensive on the CPU.
- Implemented multiprocessing to utilize the available CPU cores on an M3-6y30, but now there is an error with "write queue is full". Based on a quick search, it is most likely due to the version of MediaMTX used by wyze-bridge. The next update should bump the version of MediaMTX where the issue should be resolved.
# Future Work
- Add continuous recording
- Handle multiple RTSP streams (will depend on hardware)
- Modify to use environment variables in Docker so variables are not hard-coded in Python
