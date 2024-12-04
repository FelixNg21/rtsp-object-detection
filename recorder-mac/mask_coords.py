import cv2
import numpy as np
import argparse

# List to store points
points = []

# Mouse callback function to draw the polygon
def draw_polygon(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        if len(points) > 1:
            cv2.line(image, points[-2], points[-1], (0, 255, 0), 2)
        cv2.imshow("Image", image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Path to a video produced by the docker-wyze-bridge.", type=str, required=True)
    args = parser.parse_args()

    video = args.video
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        print("Error opening video file")
        exit(1)

    # Read the first frame
    ret, frame = cap.read()
    if not ret:
        print("Error reading video file")
        exit(1)


    # Create a copy of the frame
    clone = frame.copy()
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", draw_polygon)

    while True:
        cv2.imshow("Image", frame)
        key = cv2.waitKey(1) & 0xFF

        # Press 'r' to reset the drawing
        if key == ord('r'):
            image = clone.copy()
            points = []

        # Press 'q' to quit and save the mask
        elif key == ord('q'):
            break

    # Create a mask from the points
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    if len(points) > 2:
        cv2.fillPoly(mask, [np.array(points)], 255)

    # Save the mask coordinates
    mask_coords = points

    # Save the mask image
    cv2.imwrite('mask.png', mask)

    cv2.destroyAllWindows()

    print("Mask coordinates:", mask_coords)
