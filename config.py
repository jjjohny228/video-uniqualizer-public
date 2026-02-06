import os
import sys
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOTTOM_VIDEO = 'bottom_videos'
    RESULT_FOLDER = 'result_videos'
    SOURCE_FOLDER = 'source_videos'
    TEMP_FOLDER = 'temp'

    # Improves rendering
    if sys.platform == 'darwin':
        VIDEO_CODEC = 'h264_videotoolbox'
    # Works only for amd
    elif sys.platform == 'win32':
        VIDEO_CODEC = 'h264_amf'
    else:
        VIDEO_CODEC = 'libx264'

