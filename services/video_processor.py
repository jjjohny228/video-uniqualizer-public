import os
import random
import subprocess
import time
from typing import Optional, List
from uuid import uuid4

from config import Config, logger
from services.audio_service import get_video_duration

def trim_video(input_file: str, duration: int, start_time: Optional[int] = None, 
               used_start_time: Optional[List[int]] = None) -> str:
    """Cut random part of the video. Result video's duration equals audio duration"""
    output_file = f'temp/{uuid4()}.mp4'
    video_duration = get_video_duration(input_file)
    right_end = int(video_duration - duration)
    
    if right_end < 0:
        logger.warning(f"Video duration ({video_duration}s) is shorter than required duration ({duration}s)")
        right_end = 0
    
    # Calculate random start time
    if start_time is not None:
        video_start_time = start_time
    else:
        video_start_time = random.randint(0, max(0, right_end))
        if used_start_time:
            while video_start_time in used_start_time and right_end > 0:
                video_start_time = random.randint(0, right_end)

    command = [
        'ffmpeg',
        '-ss', str(video_start_time),
        '-i', input_file,
        '-t', str(duration),
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-y', output_file
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        logger.debug(f"Trimmed video: {input_file} -> {output_file} (start: {video_start_time}s, "
                     f"duration: {duration}s)")
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error trimming video {input_file}: {e}")
        raise


def combine_videos(source_video: str, background_video: str, target_folder: str) -> str:
    """Combine source video with background video vertically"""
    logger.info(f"Combining videos: {source_video} + {background_video}")
    
    source_video_duration = get_video_duration(source_video)
    output_video = os.path.join(target_folder, f'{int(time.time())}{os.path.basename(source_video)}')
    trimmed_bottom_video = trim_video(background_video, source_video_duration)
    
    command = [
        'ffmpeg',
        '-i', source_video,
        '-i', trimmed_bottom_video,
        '-filter_complex',
        '[0:v]crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=1080:960[v1];'
        '[1:v]crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=1080:960[v2];'
        '[v1][v2]vstack=inputs=2[v]',
        '-map', '[v]',
        '-map', '0:a?',
        '-c:v', Config.VIDEO_CODEC,
        '-c:a', 'aac',
        '-r', '30',
        '-y',
        output_video
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"Videos combined successfully: {output_video}")
        
        # Cleanup temporary trimmed video
        if os.path.exists(trimmed_bottom_video):
            os.remove(trimmed_bottom_video)
        
        return output_video
    except subprocess.CalledProcessError as e:
        logger.error(f"Error combining videos: {e}")
        # Cleanup on error
        if os.path.exists(trimmed_bottom_video):
            os.remove(trimmed_bottom_video)
        raise


def add_subtitles_to_video(video_path: str, subtitles_file: str) -> str:
    """Add subtitles to video file"""
    logger.info(f"Adding subtitles to video: {video_path}")
    
    output_file = f'temp/{uuid4()}.mp4'

    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"ass='{subtitles_file}'",
        '-c:v', Config.VIDEO_CODEC,
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-y',
        output_file
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"Subtitles added successfully: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error adding subtitles to {video_path}: {e}")
        raise
