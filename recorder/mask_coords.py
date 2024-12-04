import cv2
import numpy as np

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


# Load the image
image = cv2.imread('output_image.jpg')
clone = image.copy()
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", draw_polygon)

while True:
    cv2.imshow("Image", image)
    key = cv2.waitKey(1) & 0xFF

    # Press 'r' to reset the drawing
    if key == ord('r'):
        image = clone.copy()
        points = []

    # Press 'q' to quit and save the mask
    elif key == ord('q'):
        break

# Create a mask from the points
mask = np.zeros(image.shape[:2], dtype=np.uint8)
if len(points) > 2:
    cv2.fillPoly(mask, [np.array(points)], 255)

# Save the mask coordinates
mask_coords = points

# Save the mask image
cv2.imwrite('mask.png', mask)

cv2.destroyAllWindows()

print("Mask coordinates:", mask_coords)
