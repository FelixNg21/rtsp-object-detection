This branch represents the necessary configuration needed for deployment on a M series Mac.
I originally intended to use my original Docker container for deployment, but Docker on Mac
does not have access to the GPU, rendering the container useless for this project.

I have made modifications to run on my M1 Macbook Pro with Metal Performance Shaders (MPS)
and they are sufficient for the project to run. The Wyze-Bridge is currently set up to record
in 60 second intervals and the M1 chip is able to process each new video clip in under 60
seconds. The project is able to run in near real time except with the 1 minute delay since 
the clip is produced every minute.

I will explore longer clip segments, but if I'm trying to keep the project as close to real 
time, keeping the segments at 60 seconds is the best option.