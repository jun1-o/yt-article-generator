from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import requests
import logging
import re


def fix_typo(text: str) -> str:
    """Clean up common punctuation and spacing issues in transcripts."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" ([、。！？])", r"\1", text)
    text = re.sub(r"[、]{2,}", "、", text)
    text = re.sub(r"[。]{2,}", "。", text)
    text = text.replace("AI は", "AIは").replace("機械 学習", "機械学習")
    return text.strip()


def get_transcript(video_id: str) -> str:
    """Fetch transcript text for a given YouTube video ID and clean it."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ja", "en"])
        text = " ".join(item["text"] for item in transcript)
        return fix_typo(text)
    except (
        TranscriptsDisabled,
        NoTranscriptFound,
        CouldNotRetrieveTranscript,
        requests.exceptions.RequestException,
    ) as e:
        logging.warning("Transcript fetch failed: %s", e)
        return ""
