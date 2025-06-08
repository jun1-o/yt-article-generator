
def generate_article(title: str, summary: str, context: str) -> str:
    """Return article text in a simple note-like format."""
    parts = [
        f"# {title}",
        "\n## Summary",
        summary,
        "\n## Additional Context",
        context,
        "\n## Thoughts",
        "Thank you for reading!",
    ]
    return "\n\n".join(parts)
