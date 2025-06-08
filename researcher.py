import wikipedia


def get_wikipedia_info(query: str) -> str:
    """Return the first three paragraphs of a Wikipedia search result."""
    wikipedia.set_lang("en")
    try:
        page = wikipedia.page(query)
    except wikipedia.exceptions.DisambiguationError as e:
        page = wikipedia.page(e.options[0])
    content = page.content.split('\n\n')
    return '\n\n'.join(content[:3])
