import subprocess
from typing import Optional
from uuid import uuid4

from config import logger


def extract_audio(input_video: str) -> Optional[str]:
    """Extract audio from video file"""
    output_audio = f'temp/{uuid4()}.mp3'

    command = [
        'ffmpeg',
        '-i', input_video,
        '-q:a', '0',
        '-map', 'a',
        '-y', output_audio
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"Audio extracted successfully: {output_audio}")
        return output_audio
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting audio from {input_video}: {e}")
        return None
    except FileNotFoundError:
        logger.error("FFmpeg not found. Please install FFmpeg.")
        return None


def get_audio_duration(audio_path: str) -> Optional[float]:
    """Get audio duration in seconds using ffprobe"""
    command = [
        'ffprobe',
        '-i', audio_path,
        '-hide_banner',
        '-loglevel', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except (ValueError, subprocess.CalledProcessError) as e:
        logger.error(f"Error determining audio duration for {audio_path}: {e}")
        return None


def get_video_duration(video_path: str) -> float:
    """Get the duration of the video in seconds"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            text=True
        )
        return float(result.stdout.strip())
    except (ValueError, subprocess.CalledProcessError) as e:
        logger.error(f"Error getting video duration for {video_path}: {e}")
        raise
