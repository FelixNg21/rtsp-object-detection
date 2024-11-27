from os import getenv, makedirs
from config_utils import get_env_list

# RTSP_URL = getenv("RTSP_URL")
# RTSP_CAM_NAME = get_env_list(getenv("RTSP_CAM_NAME"))
# DAY_THRESHOLD = int(getenv("DAY_THRESHOLD", 7))

MODEL_NAME = getenv("MODEL_NAME", "yolo11n.pt")
MOVEMENT_THRESHOLD = int(getenv("MOVEMENT_THRESHOLD", 15))
DELAY_TIME = int(getenv("DELAY_TIME", 15))


VIDEO_SOURCE = getenv("VIDEO_SOURCE", "/Users/felixng/Desktop/RTSP_cam/rtsp-object-detection/videos")
CLIP_DEST = getenv("CLIP_DEST", "/Users/felixng/Desktop/RTSP_cam/rtsp-object-detection/clips")


MASK_COORDS = [(0, 0), (0, 733), (781, 695), (1110, 651), (1505, 597), (1630, 593), (1595, 0)]