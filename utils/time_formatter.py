def format_time(seconds: int) -> str:
    """Format seconds to ASS subtitle time format (HH:MM:SS.CS)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)
    return f"{hours:02}:{minutes:02}:{secs:02}.{centiseconds:02}"
