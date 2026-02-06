"""Web page loader using httpx + BeautifulSoup."""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from app.ingestion.loaders.base import LoadedDocument
from app.ingestion.loaders.url_validator import SSRFError, validate_url

_MAX_REDIRECTS = 5


class WebLoader:
    @property
    def supported_extensions(self) -> list[str]:
        return []

    def load(self, source_uri: str) -> list[LoadedDocument]:
        validate_url(source_uri)

        url = source_uri
        for _ in range(_MAX_REDIRECTS):
            response = httpx.get(url, timeout=30, follow_redirects=False)
            if response.is_redirect:
                url = str(response.next_request.url)
                validate_url(url)
                continue
            response.raise_for_status()
            break
        else:
            raise SSRFError(f"Too many redirects (>{_MAX_REDIRECTS}) for {source_uri}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script/style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        title = soup.title.string if soup.title else source_uri
        text = soup.get_text(separator="\n", strip=True)

        return [
            LoadedDocument(
                text=text,
                metadata={"title": str(title), "source_type": "web", "url": source_uri},
                source_uri=source_uri,
            )
        ]
