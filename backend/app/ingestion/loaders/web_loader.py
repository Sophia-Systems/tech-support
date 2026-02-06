"""Web page loader using httpx + BeautifulSoup."""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from app.ingestion.loaders.base import LoadedDocument


class WebLoader:
    @property
    def supported_extensions(self) -> list[str]:
        return []

    def load(self, source_uri: str) -> list[LoadedDocument]:
        response = httpx.get(source_uri, timeout=30, follow_redirects=True)
        response.raise_for_status()

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
