import os
import yaml
from typing import Optional
import openai
import re


_DEF_CONFIG_PATHS = [".env", "config/settings.yaml"]


def _load_api_key() -> Optional[str]:
    """Load OpenAI API key from environment or config files."""
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    for path in _DEF_CONFIG_PATHS:
        if os.path.exists(path):
            if path.endswith('.env'):
                try:
                    from dotenv import load_dotenv
                    load_dotenv(path)
                    key = os.getenv("OPENAI_API_KEY")
                    if key:
                        return key
                except Exception:
                    pass
            else:
                try:
                    with open(path, 'r') as f:
                        data = yaml.safe_load(f) or {}
                    key = data.get('OPENAI_API_KEY')
                    if key:
                        return key
                except Exception:
                    pass
    return None


def summarize_text(text: str) -> str:
    """Summarize the provided text using OpenAI ChatGPT API."""
    api_key = _load_api_key()

    if api_key:
        openai.api_key = api_key
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes transcripts.",
            },
            {"role": "user", "content": text},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    # Fallback mock summarization when no API key is available
    sentences = re.split(r"(?<=[。！？])", text)
    return "".join(sentences[:3]).strip()
