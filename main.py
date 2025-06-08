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
    parser.add_argument('--out', help='File path to save the generated article')
    parser.add_argument(
        '--skip-summary',
        action='store_true',
        help='Skip the summarization step and use raw transcript',
    )
    parser.add_argument(
        '--skip-research',
        action='store_true',
        help='Skip the Wikipedia research step',
    )
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    print(f"[🎥 Video ID] {video_id}")

    transcript = get_transcript(video_id)
    print(f"[📜 Transcript] {transcript[:100]}...")

    if args.skip_summary:
        summary = transcript
    else:
        summary = summarize_text(transcript)
    print(f"[📝 Summary] {summary[:100]}...")

    if args.skip_research:
        context = ""
    else:
        context = get_wikipedia_info(args.topic)
    print(f"[🔍 Wikipedia] {context[:100]}...")

    article = generate_article(args.topic, summary, context)
    print("\n[📄 最終記事]\n", article)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(article)
            print(f"[💾 Saved] Article written to {args.out}")
        except OSError as e:
            print(f"[⚠️ Save failed] {e}")


if __name__ == '__main__':
    main()
