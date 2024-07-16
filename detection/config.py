from os import getenv, makedirs
from config_utils import get_env_list

RTSP_URL = getenv("RTSP_URL")
RTSP_CAM_NAME = get_env_list(getenv("RTSP_CAM_NAME"))
MODEL_NAME = getenv("MODEL_NAME", "yolov8n.pt")
MOVEMENT_THRESHOLD = int(getenv("MOVEMENT_THRESHOLD", 15))
DELAY_TIME = int(getenv("DELAY_TIME", 10))

DAY_THRESHOLD = int(getenv("DAY_THRESHOLD", 7))

VIDEO_DIR = getenv("VIDEO_DIR", "videos")