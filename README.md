# rtsp-object-detection

This branch is a "deployable" version.
The project was inspired by recent events in my neighbourhood with several break-ins and other police incidents where I was requested to provide any available footage. 
Unfortunately, I use Wyze cameras around the house and over time they have been moving free features behind a subscription service. 

The program uses opencv and yolov8 to detect motion in an RTSP stream and create video clips. It depends on https://github.com/mrlt8/docker-wyze-bridge to provide the RTSP stream.

A docker-compose.yml has been provided so I can deploy on my other devices. It works fine on my main PC, but I would prefer to have it run 24/7 on an old laptop, but the anemic M3-6y30 4 core CPU runs into issues.
I'll look into a mini-PC or scraping together some sort of HomeLab server.

# Future Work
- Add continuous recording
- Handle multiple RTSP streams (will depend on hardware)
- Modify to use environment variables in Docker so variables are not hard-coded in Python
