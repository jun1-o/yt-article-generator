# 🧠 yt-article-generator

This Python tool transforms a YouTube video into a summarized, researched, and structured article.
Perfect for blog writers, note creators, and SEO-focused content generation.

## ✅ Features
- Auto fetch subtitles via `youtube-transcript-api`
- Summarize with OpenAI GPT
- Research related terms via Wikipedia
- Auto-generate articles in note-style format
- Optional flags to skip summarization or research

## 📦 Install

```bash
pip install -r requirements.txt
```

## 🚀 Usage

First set your OpenAI API key to enable GPT summarization:

```bash
export OPENAI_API_KEY=your-key
python main.py --url <YouTube_URL> --topic "AI教育" --out article.txt
```

If the `OPENAI_API_KEY` variable is unset, the script falls back to a short summary:

```bash
unset OPENAI_API_KEY
python main.py --url <YouTube_URL> --topic "AI教育"
```

You can also skip specific steps when running the tool:

```bash
python main.py --url <YouTube_URL> --topic "AI教育" --skip-summary   # skip summarization
python main.py --url <YouTube_URL> --topic "AI教育" --skip-research  # skip Wikipedia lookup
```
