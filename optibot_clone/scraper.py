import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_markdown
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass(frozen=True)
class Article:
    id: int
    title: str
    slug: str
    url: str
    html: str
    updated_at: str


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "article"


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
def _get_json(url: str) -> dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_articles(base_url: str, locale: str, limit: int) -> list[Article]:
    articles: list[Article] = []
    url = f"{base_url}/api/v2/help_center/{locale}/articles.json?per_page=100"

    while url and len(articles) < limit:
        payload = _get_json(url)
        for item in payload.get("articles", []):
            if item.get("draft"):
                continue
            title = item.get("title") or f"article-{item['id']}"
            articles.append(
                Article(
                    id=int(item["id"]),
                    title=title,
                    slug=f"{item['id']}-{slugify(title)}",
                    url=item.get("html_url") or item.get("url"),
                    html=item.get("body") or "",
                    updated_at=item.get("updated_at") or "",
                )
            )
            if len(articles) >= limit:
                break
        url = payload.get("next_page")

    return articles


def fetch_article_by_id(base_url: str, article_id: int) -> Article:
    payload = _get_json(f"{base_url}/api/v2/help_center/articles/{article_id}.json")
    item = payload["article"]
    title = item.get("title") or f"article-{item['id']}"
    return Article(
        id=int(item["id"]),
        title=title,
        slug=f"{item['id']}-{slugify(title)}",
        url=item.get("html_url") or item.get("url"),
        html=item.get("body") or "",
        updated_at=item.get("updated_at") or "",
    )


def article_to_markdown(article: Article) -> str:
    soup = BeautifulSoup(article.html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    body = html_to_markdown(str(soup), heading_style="ATX", bullets="-").strip()
    body = re.sub(r"\n{3,}", "\n\n", body)

    return (
        f"# {article.title}\n\n"
        f"Article URL: {article.url}\n\n"
        f"Last Updated: {article.updated_at}\n\n"
        f"{body}\n"
    )


def content_hash(markdown: str) -> str:
    return hashlib.sha256(markdown.encode("utf-8")).hexdigest()


def iter_markdown_articles(articles: Iterable[Article]) -> Iterable[tuple[Article, str, str]]:
    for article in articles:
        markdown = article_to_markdown(article)
        yield article, markdown, content_hash(markdown)
