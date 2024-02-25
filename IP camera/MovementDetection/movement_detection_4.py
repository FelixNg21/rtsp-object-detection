import cv2
import numpy as np
from datetime import datetime

# RTSP URL of the camera feed
rtsp_url = "rtsp://localhost:8554/driveway"

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url)

# Create a background subtractor (MOG2 in this case)
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

# Parameters for motion detection
area_threshold = 8000  # Minimum area for considering an object as motion
motion_detected = False
motion_start_time = None

# Parameters for recording
warmup_time = 5  # Time to allow the camera to warm up before recording
warmup_frames = []
video_writer = None
fps = cap.get(5)
fourcc = cv2.VideoWriter.fourcc(*'XVID')


# Main loop
while True:
    ret, frame = cap.read()

    if not ret:
        print("Error reading frame from the video stream.")
        break

    # Convert frame to grayscale for background subtraction
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply background subtraction
    fg_mask = bg_subtractor.apply(gray_frame)

    # Perform thresholding and morphology to get a clean motion mask
    _, thresh = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
    motion_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=2)

    # Find contours in the motion mask
    contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Filter contours based on area
        if cv2.contourArea(contour) > area_threshold:
            # Motion detected
            if not motion_detected:
                print("Motion detected!")
                motion_detected = True
                motion_start_time = datetime.now()

                # Start recording or take other action here
                video_filename = f"motion_{datetime.now().strftime('%Y%m%d%H%M%S')}.avi"
                video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (frame.shape[1], frame.shape[0]))

            # Draw bounding box around the detected motion
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Write the frame to the video file
    if video_writer is not None:
        video_writer.write(frame)

    # If motion is detected and a certain time has passed, stop recording
    if motion_detected and (datetime.now() - motion_start_time).total_seconds() > 20:
        # Stop recording after 5 seconds of inactivity
        motion_detected = False
        recording = False
        video_writer.release()

    # Display the frame
    cv2.imshow('Motion Detection', frame)

    # Check for user exit
    if cv2.waitKey(30) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release the VideoCapture and close windows
cap.release()
cv2.destroyAllWindows()
