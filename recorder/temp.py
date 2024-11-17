import cv2
import numpy as np

def grab_still_image(video_path, frame_number, output_image_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Set the frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frame
    ret, frame = cap.read()

    if ret:
        # Save the frame as an image
        cv2.imwrite(output_image_path, frame)
        print(f"Frame {frame_number} saved as {output_image_path}")
    else:
        print(f"Error: Could not read frame {frame_number}.")

    # Release the video capture object
    cap.release()


# Example usage
# video_path = "C:\\Users\Felix\Desktop\Camera\clips\\2024\\11\\05\\2024-11-05_19-15-23.mp4"
# frame_number = 1  # Frame number to capture
# output_image_path = 'output_image.jpg'
# grab_still_image(video_path, frame_number, output_image_path)



# image_path = r"C:\Users\Felix\Desktop\Camera\rtsp-object-detection\recorder\output_image.jpg"
# image = cv2.imread(image_path)
# mask = np.zeros((1080, 1920), dtype=np.uint8)
# mask_coords = [(0, 0), (0, 733), (781, 695), (1110, 651), (1505, 597), (1630, 593), (1595, 0)]
# cv2.fillPoly(mask, [np.array(mask_coords)], 255)
#
# inverted_mask = cv2.bitwise_not(mask)
# result = cv2.bitwise_and(image, image, mask=inverted_mask)
#
#
# # Display the images
# # cv2.imshow('Image', image)
# cv2.imshow('Mask', mask)
# # cv2.imshow('Inverted Mask', inverted_mask)
# # cv2.imshow('Result', result)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

filename_str = "videos/driveway/2024-11-04/driveway_14_05_52.mp4"
filename_str_split = filename_str.split("/")
print(filename_str_split)
date = filename_str_split[2]
print(date)
time_h = filename_str_split[3].split("_")[1]
time_s = filename_str_split[3].split("_")[2]
time_ms = filename_str_split[3].split("_")[3].split(".")[0]
print(time_h, time_s, time_ms)