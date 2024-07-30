import cv2
import numpy as np

# Step 1: Capture the RTSP Stream
# rtsp_url = "rtsp://your_rtsp_stream_url"
# cap = cv2.VideoCapture(rtsp_url)

cap = cv2.VideoCapture("test_clip.mp4")

# Initialize variables for motion detection
ret, frame1 = cap.read()
ret, frame2 = cap.read()

while cap.isOpened():
    # Step 2: Detect Motion
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Step 3: Create a Motion Mask
    mask = np.zeros_like(frame1)
    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(mask, (x, y), (w, h), (255, 255, 255), -1)

    # Step 4: Apply the Motion Mask
    masked_frame = cv2.bitwise_and(frame1, mask)

    # Step 5: Send to YOLO Model
    # Assuming you have a function `detect_objects` that takes a frame and returns detections
    # detections = detect_objects(masked_frame)

    # Display the result
    cv2.imshow("Masked Frame", masked_frame)
    cv2.imshow("Original Frame", frame1)

    frame1 = frame2
    ret, frame2 = cap.read()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
