import argparse
from urllib.parse import urlparse, parse_qs
from transcript import get_transcript
from summarizer import summarize_text
from researcher import get_wikipedia_info
from writer import generate_article


def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL."""
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path.lstrip('/')
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [''])[0]
        if parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
        if parsed.path.startswith('/v/'):
            return parsed.path.split('/')[2]
    raise ValueError('Invalid YouTube URL')


def main():
    parser = argparse.ArgumentParser(description='Generate note-style article from YouTube')
    parser.add_argument('--url', required=True, help='YouTube video URL')
    parser.add_argument('--topic', required=True, help='Research topic for Wikipedia')
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    transcript = get_transcript(video_id)
    summary = summarize_text(transcript)
    context = get_wikipedia_info(args.topic)
    article = generate_article(args.topic, summary, context)
    print(article)


if __name__ == '__main__':
    main()
