
def generate_article(title: str, summary: str, context: str) -> str:
    """Return article text formatted for note."""
    parts = [
        f"# タイトル：{title}",
        "",
        "## \U0001F4CC 要約ポイント（3行で）",
        summary,
        "",
        "## \U0001F9E0 詳細解説と補足知識",
        context,
        "",
        "## \u2728 まとめと感想",
        "（あとで追記可）",
    ]
    return "\n".join(parts)
