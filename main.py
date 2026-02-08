import os
import random
import shutil
import subprocess
import time
from typing import Optional
from uuid import uuid4
from openai import OpenAI

from config import Config


def extract_audio(input_video: str):
    # Ensure the output file has a valid audio extension
    output_audio = f'temp/{uuid4()}.mp3'

    # FFmpeg command to extract audio
    command = [
        'ffmpeg',
        '-i', input_video,
        '-q:a', '0',
        '-map', 'a',
        '-y', output_audio
    ]

    try:
        # Run the FFmpeg command
        subprocess.run(command, check=True)
        print(f"Audio extracted successfully: {output_audio}")
        return output_audio
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while extracting audio: {e}")


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)
    return f"{hours:02}:{minutes:02}:{secs:02}.{centiseconds:02}"


def subtitles_from_audio(file: str, language_code: str):
    client = OpenAI()
    with open(file, 'rb') as media_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=media_file,
            temperature=0.2,
            language=language_code,
            response_format="verbose_json",
            timestamp_granularities=['word']
        )

    transcript_dict = transcript.to_dict()  # или transcript.dict()
    words = transcript_dict.get("words", [])

    ass_header = """[Script Info]
Title: Generated ASS file
ScriptType: v4.00+


[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,20,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    subtitles = [ass_header]

    for word in words:
        start_time = format_time(word.get('start'))
        end_time = format_time(word.get('end'))
        text = word.get('word')

        subtitle_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
        subtitles.append(subtitle_line)

    ass_file = f'temp/{uuid4()}.txt'
    with open(ass_file, 'w', encoding='utf-8') as f:
        f.writelines(subtitles)

    return ass_file


def get_audio_duration(audio_path):
    # Используем ffprobe для получения продолжительности аудио
    command = [
        'ffprobe',
        '-i', audio_path,  # Входной файл аудио
        '-hide_banner',  # Скрыть ненужную информацию
        '-loglevel', 'error',  # Скрыть ненужные ошибки
        '-show_entries', 'format=duration',  # Показать только продолжительность
        '-of', 'default=noprint_wrappers=1:nokey=1'  # Вывод только значения
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    # Если успешно получили данные, возвращаем продолжительность в секундах
    try:
        duration = float(result.stdout.strip())
        return duration
    except ValueError:
        print("Error: Could not determine audio duration.")
        return None


def add_subtitles_to_video(video_path, subtitles_file):
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

    subprocess.run(command)
    return output_file


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
    return output_video


if __name__ == '__main__':
    ADD_SUBTITLES = True
    source_video_folder = 'source_videos'
    result_video_folder = 'result_videos'
    bottom_video_folder = 'bottom_videos'
    bottom_videos = os.listdir(bottom_video_folder)

    source_videos = os.listdir(source_video_folder)

    for video in source_videos:
        full_video_path = os.path.join(source_video_folder, video)
        random_bottom_video_path = os.path.join(bottom_video_folder, random.choice(bottom_videos))
        combined_video = combine_videos(full_video_path, random_bottom_video_path, Config.RESULT_FOLDER)
        if ADD_SUBTITLES:
            audio_from_video = extract_audio(combined_video)
            subtitles_file = subtitles_from_audio(audio_from_video, 'en')
            result = add_subtitles_to_video(combined_video, subtitles_file)
            shutil.move(result, os.path.join(result_video_folder, f'{int(time.time())}.mp4'))
            os.remove(audio_from_video)
            os.remove(subtitles_file)
        os.remove(full_video_path)
