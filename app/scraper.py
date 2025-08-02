import requests
from bs4 import BeautifulSoup
import re

BLOCK_TAGS = ['script', 'style', 'noscript', 'header', 'footer', 'svg', 'img', 'aside', 'nav', 'form', 'input']

def fetch_text_from_url(url: str, max_length=15_000) -> str:
    """Download and clean HTML, return main text (truncated)."""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        return f"Failed to retrieve page: {e}"
    soup = BeautifulSoup(resp.text, 'html.parser')
    for t in BLOCK_TAGS:
        for tag in soup.find_all(t):
            tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    text = re.sub(r"\n{2,}", "\n", text)  # collapse blank lines
    return text[:max_length]
