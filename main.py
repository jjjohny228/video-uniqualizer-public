import os
import random
import shutil
import time
from typing import List

from config import Config, logger
from services.audio_service import extract_audio
from services.subtitle_service import subtitles_from_audio
from services.video_processor import combine_videos, add_subtitles_to_video


def process_videos(add_subtitles: bool = True) -> None:
    """Process all videos from source folder"""
    Config.ensure_folders_exist()
    
    source_videos: List[str] = [f for f in os.listdir(Config.SOURCE_FOLDER) 
                                if os.path.isfile(os.path.join(Config.SOURCE_FOLDER, f))]
    bottom_videos: List[str] = [f for f in os.listdir(Config.BOTTOM_VIDEO) 
                                 if os.path.isfile(os.path.join(Config.BOTTOM_VIDEO, f))]
    
    if not source_videos:
        logger.warning(f"No videos found in {Config.SOURCE_FOLDER}")
        return
    
    if not bottom_videos:
        logger.error(f"No background videos found in {Config.BOTTOM_VIDEO}")
        return
    
    logger.info(f"Found {len(source_videos)} source video(s) to process")
    
    for video in source_videos:
        try:
            full_video_path = os.path.join(Config.SOURCE_FOLDER, video)
            random_bottom_video_path = os.path.join(Config.BOTTOM_VIDEO, random.choice(bottom_videos))
            
            logger.info(f"Processing video: {video}")
            combined_video = combine_videos(full_video_path, random_bottom_video_path, Config.TEMP_FOLDER)
            final_output = os.path.join(Config.RESULT_FOLDER, f'{int(time.time())}.mp4')
            
            if add_subtitles:
                logger.info(f"Adding subtitles to: {video}")
                audio_from_video = extract_audio(combined_video)
                if audio_from_video:
                    subtitles_file = subtitles_from_audio(audio_from_video)
                    result = add_subtitles_to_video(combined_video, subtitles_file)
                    shutil.move(result, final_output)
                    logger.info(f"Final video saved: {final_output}")
                    
                    # Cleanup temporary files
                    if os.path.exists(audio_from_video):
                        os.remove(audio_from_video)
                    if os.path.exists(subtitles_file):
                        os.remove(subtitles_file)
                else:
                    shutil.move(combined_video, final_output)
                    logger.error(f"Failed to extract audio from {combined_video}")

            if os.path.exists(combined_video):
                os.remove(combined_video)
            
            # Remove processed source video
            if os.path.exists(full_video_path):
                os.remove(full_video_path)
                logger.info(f"Removed processed source video: {video}")
                
        except Exception as e:
            logger.error(f"Error processing video {video}: {e}", exc_info=True)


if __name__ == '__main__':
    process_videos(add_subtitles=Config.ADD_SUBTITLES)
