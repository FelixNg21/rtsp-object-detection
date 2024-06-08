from os import getenv, makedirs
from config_utils import get_env_list

RTSP_URL = getenv("RTSP_URL")
RTSP_CAM_NAME = get_env_list("RTSP_CAM_NAME")