import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class Config:
    # Folder paths
    BOTTOM_VIDEO = 'bottom_videos'
    RESULT_FOLDER = 'result_videos'
    SOURCE_FOLDER = 'source_videos'
    TEMP_FOLDER = 'temp'

    ASS_HEADER_PATH = 'resource/ass_header.txt'

    ADD_SUBTITLES = os.getenv('ADD_SUBTITLES').lower() in ('true', '1', 'yes', 'on')

    # Video codec selection based on platform
    # Improves rendering performance
    if sys.platform == 'darwin':
        VIDEO_CODEC = 'h264_videotoolbox'
    # Works only for AMD
    elif sys.platform == 'win32':
        VIDEO_CODEC = 'h264_amf'
    else:
        VIDEO_CODEC = 'libx264'

    @staticmethod
    def ensure_folders_exist() -> None:
        """Create necessary folders if they don't exist"""
        folders = [
            Config.BOTTOM_VIDEO,
            Config.RESULT_FOLDER,
            Config.SOURCE_FOLDER,
            Config.TEMP_FOLDER
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            logger.info(f"Ensured folder exists: {folder}")
