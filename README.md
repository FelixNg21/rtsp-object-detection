# rtsp-object-detection

This branch is a "deployable" version.
The project was inspired by recent events in my neighbourhood with several break-ins and other police incidents where I was requested to provide any available footage. 
Unfortunately, I use Wyze cameras around the house and over time they have been moving free features behind a subscription service. 

The program uses opencv and yolov8 to detect motion in an RTSP stream and create video clips. It depends on https://github.com/mrlt8/docker-wyze-bridge to provide the RTSP stream.


# Experiments
- Attempted to use a substream provided by the docker-wyze-bridge, but it was out of sync with the main stream. This resulted in the bounding boxes being off by several seconds. I had thought that tracking based on a lower resolution image would be less intensive on the CPU.
- Implemented multiprocessing to utilize the available CPU cores on an M3-6y30, but now there is an error with "write queue is full". Based on a quick search, it is most likely due to the version of MediaMTX used by wyze-bridge. The next update should bump the version of MediaMTX where the issue should be resolved.
# Future Work
  - UPDATE: as my old laptop is not powerful enough to run inference quickly enough, work has been paused until I find another solution to run the program. I would prefer not to have to run on my main machine, but the program otherwise works on that machine.
- Add continuous recording
- Handle multiple RTSP streams (will depend on hardware)
- Modify to use environment variables in Docker so variables are not hard-coded in Python



