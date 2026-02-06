import os
import random
import subprocess
import time
from typing import Optional
from uuid import uuid4

from config import Config


def get_video_duration(video_path):
    """Get the duration of the video in seconds."""
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)


def trim_video(input_file: str, duration: int, start_time: Optional[int] = None, used_start_time: Optional[list] = None):
    """
    This function cuts random part of the video. Result video's duration equals audio duration
    """
    output_file = f'temp/{uuid4()}.mp4'
    video_duration = get_video_duration(input_file)
    right_end = int(video_duration - duration)
    # Calculate random start time
    if start_time:
        video_start_time = start_time
    else:
        video_start_time = random.randint(0, right_end)
        if used_start_time:
            while video_start_time in used_start_time:
                video_start_time = random.randint(0, right_end)

        # Build the ffmpeg command
        command = [
            'ffmpeg',
            '-ss', str(video_start_time),  # Start time in seconds
            '-i', input_file,  # Input file
            '-t', str(duration),  # Duration in seconds
            '-c:v', 'copy',  # Copy video codec (maintain quality)
            '-c:a', 'copy',  # Copy audio codec (maintain quality)
            '-y', output_file  # Output file
        ]

        # Run the command
        subprocess.run(command, check=True)
        return output_file


def combine_videos(source_video, background_video, target_folder):
    # Получаем длительность первого видео
    source_video_duration = get_video_duration(source_video)
    output_video = os.path.join(target_folder, f'{int(time.time())}{os.path.basename(source_video)}')
    trimmed_bottom_video = trim_video(background_video, source_video_duration)
    # Команда FFmpeg для обработки видео
    command = [
        'ffmpeg',
        '-i', source_video, # Первое видео
        '-i', trimmed_bottom_video,  # Второе видео
        '-filter_complex',
        # Вырезаем квадрат в центре первого видео и масштабируем до 960x1080
        '[0:v]crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=1080:960[v1];'
        # Вырезаем квадрат в центре второго видео и масштабируем до 960x1080
        f'[1:v]crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=1080:960[v2];'
        # Накладываем видео друг на друга вертикально
        '[v1][v2]vstack=inputs=2[v]',
        # '[stacked]scale=1080:1920[v]',
        '-map', '[v]',  # Используем результат наложения
        '-map', '0:a?',  # Используем аудио из первого видео (если есть)
        '-c:v', Config.VIDEO_CODEC,  # Кодек для видео
        '-c:a', 'aac',# Ограничиваем длительность по первому видео
        '-r', '30',
        '-y',
        output_video
    ]

    # Запускаем команду
    subprocess.run(command)
    os.remove(trimmed_bottom_video)


if __name__ == '__main__':
    source_video_folder = 'source_videos'
    result_video_folder = 'result_videos'
    bottom_video_folder = 'bottom_videos'
    bottom_videos = os.listdir(bottom_video_folder)

    source_videos = os.listdir(source_video_folder)

    for video in source_videos:
        full_video_path = os.path.join(source_video_folder, video)
        random_bottom_video_path = os.path.join(bottom_video_folder, random.choice(bottom_videos))
        combine_videos(full_video_path, random_bottom_video_path, Config.RESULT_FOLDER)
        os.remove(full_video_path)
