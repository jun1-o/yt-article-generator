import os
import logging
from openai import OpenAI
import re


def summarize_text(text: str) -> str:
    """Summarize the provided text using OpenAI ChatGPT API."""
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes transcripts.",
                },
                {"role": "user", "content": text},
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.warning("OpenAI API failed: %s", e)

    # Fallback mock summarization when no API key is available
    sentences = re.split(r"(?<=[。！？])", text)
    return "".join(sentences[:3]).strip()
