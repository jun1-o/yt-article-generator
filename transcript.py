from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str) -> str:
    """Fetch transcript text for a given YouTube video ID."""
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join(item['text'] for item in transcript)
    return text
