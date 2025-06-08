import logging
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError, HTTPTimeoutError


def get_wikipedia_info(query: str) -> str:
    """Return the first three paragraphs of a Wikipedia search result."""
    wikipedia.set_lang("en")
    try:
        page = wikipedia.page(query)
    except DisambiguationError as e:
        page = wikipedia.page(e.options[0])
    except (PageError, HTTPTimeoutError, Exception) as e:
        logging.warning("Wikipedia fetch failed: %s", e)
        return ""

    content = page.content.split('\n\n')
    return "\n\n".join(content[:3])
