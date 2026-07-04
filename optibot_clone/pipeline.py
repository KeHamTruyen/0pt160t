from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from optibot_clone.chunking import chunk_markdown
from optibot_clone.config import Settings
from optibot_clone.gemini_store import GeminiKnowledgeStore
from optibot_clone.scraper import fetch_article_by_id, fetch_articles, iter_markdown_articles
from optibot_clone.state import read_json, write_json


def run_pipeline(settings: Settings) -> dict[str, Any]:
    docs_dir = Path(settings.docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    previous = read_json(settings.state_path)
    previous_articles = previous.get("articles", {})
    next_articles: dict[str, Any] = {}

    store = GeminiKnowledgeStore(
        api_key=settings.gemini_api_key,
        embedding_model=settings.gemini_file_search_embedding_model,
        store_name=settings.file_search_store_name
        or previous.get("file_search_store_name", ""),
        store_display_name=settings.file_search_store_display_name,
    )

    stats: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "added": 0,
        "updated": 0,
        "skipped": 0,
        "files_uploaded": 0,
        "chunks_indexed": 0,
        "file_search_store_name": "",
        "articles": [],
    }

    articles = fetch_articles(
        settings.support_base_url,
        settings.article_locale,
        settings.max_articles,
    )
    seen_ids = {article.id for article in articles}
    for article_id in settings.required_article_ids:
        if article_id not in seen_ids:
            articles.append(fetch_article_by_id(settings.support_base_url, article_id))
            seen_ids.add(article_id)

    total = len(articles)
    print(f"Fetched {total} articles from {settings.support_base_url}", flush=True)

    for index, (article, markdown, digest) in enumerate(iter_markdown_articles(articles), start=1):
        article_key = str(article.id)
        old = previous_articles.get(article_key)
        path = docs_dir / f"{article.slug}.md"

        next_article = {
            "title": article.title,
            "url": article.url,
            "slug": article.slug,
            "hash": digest,
            "updated_at": article.updated_at,
            "path": str(path),
        }
        if old:
            next_article.update(
                {
                    key: value
                    for key, value in old.items()
                    if key not in next_article
                }
            )
        next_articles[article_key] = next_article

        if (
            old
            and old.get("hash") == digest
            and path.exists()
            and old.get("file_search_store_name") == store.store_name
        ):
            stats["skipped"] += 1
            print(f"[{index}/{total}] skipped: {article.title}", flush=True)
            continue

        path.write_text(markdown, encoding="utf-8")
        chunks = chunk_markdown(markdown, settings.chunk_size, settings.chunk_overlap)
        print(
            f"[{index}/{total}] indexing: {article.title} ({len(chunks)} local chunks)",
            flush=True,
        )
        upload = store.upload_to_file_search_store(path)
        next_article["file_search_store_name"] = upload["file_search_store_name"]

        if old:
            stats["updated"] += 1
            status = "updated"
        else:
            stats["added"] += 1
            status = "added"

        stats["files_uploaded"] += 1
        stats["chunks_indexed"] += len(chunks)
        stats["file_search_store_name"] = upload["file_search_store_name"]
        stats["articles"].append(
            {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "status": status,
                "chunks": len(chunks),
                "file_search": upload,
            }
        )

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_search_store_name": store.store_name,
        "articles": next_articles,
    }
    stats["file_search_store_name"] = store.store_name
    write_json(settings.state_path, state)
    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_json(settings.upload_log_path, stats)
    return stats
