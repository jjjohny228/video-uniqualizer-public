from uuid import uuid4
from openai import OpenAI
from utils.time_formatter import format_time

from config import logger, Config


def subtitles_from_audio(file: str) -> str:
    """Generate subtitles from audio file using OpenAI Whisper"""
    logger.info(f"Generating subtitles from audio: {file}")
    
    try:
        client = OpenAI()
        with open(file, 'rb') as media_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=media_file,
                temperature=0.2,
                response_format="verbose_json",
                timestamp_granularities=['word']
            )

        transcript_dict = transcript.to_dict()
        words = transcript_dict.get("words", [])
        
        logger.info(f"Transcribed {len(words)} words")
        with open(Config.ASS_HEADER_PATH, 'r') as ass_file:
            ass_header = ass_file.read()

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

        logger.info(f"Subtitles file created: {ass_file}")
        return ass_file
    except Exception as e:
        logger.error(f"Error generating subtitles from {file}: {e}", exc_info=True)
        raise
