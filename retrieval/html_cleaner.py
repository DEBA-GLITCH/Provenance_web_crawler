
from readability import Document
from lxml import html


def extract_main_content(raw_html: bytes) -> str:
    """
    Extract main readable content from raw HTML.
    Does NOT mutate stored evidence.
    Returns cleaned text.
    """

    try:
        decoded = raw_html.decode("utf-8", errors="ignore")
    except Exception:
        return ""

    try:
        doc = Document(decoded)
        main_html = doc.summary()

        tree = html.fromstring(main_html)
        text = tree.text_content()

        cleaned = "\n\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )

        return cleaned

    except Exception:
        return ""
