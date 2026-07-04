import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    support_base_url: str = "https://support.optisigns.com"
    article_locale: str = "en-us"
    max_articles: int = 30
    required_article_ids: tuple[int, ...] = (360051014713,)
    chunk_size: int = 1200
    chunk_overlap: int = 180
    gemini_model: str = "gemini-2.5-flash"
    gemini_file_search_embedding_model: str = "models/gemini-embedding-001"
    file_search_store_name: str = ""
    file_search_store_display_name: str = "optibot-support-docs"
    docs_dir: str = "data/docs"
    state_path: str = "data/state/articles.json"
    upload_log_path: str = "data/logs/last_run.json"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY", "")
        if not api_key:
            raise RuntimeError("Set GEMINI_API_KEY or API_KEY before running.")

        return cls(
            gemini_api_key=api_key,
            support_base_url=os.getenv("SUPPORT_BASE_URL", cls.support_base_url).rstrip("/"),
            article_locale=os.getenv("ARTICLE_LOCALE", cls.article_locale),
            max_articles=int(os.getenv("MAX_ARTICLES", cls.max_articles)),
            required_article_ids=tuple(
                int(value.strip())
                for value in os.getenv(
                    "REQUIRED_ARTICLE_IDS",
                    ",".join(str(article_id) for article_id in cls.required_article_ids),
                ).split(",")
                if value.strip()
            ),
            chunk_size=int(os.getenv("CHUNK_SIZE", cls.chunk_size)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", cls.chunk_overlap)),
            gemini_model=os.getenv("GEMINI_MODEL", cls.gemini_model),
            gemini_file_search_embedding_model=os.getenv(
                "GEMINI_FILE_SEARCH_EMBEDDING_MODEL",
                cls.gemini_file_search_embedding_model,
            ),
            file_search_store_name=os.getenv(
                "FILE_SEARCH_STORE_NAME", cls.file_search_store_name
            ),
            file_search_store_display_name=os.getenv(
                "FILE_SEARCH_STORE_DISPLAY_NAME",
                cls.file_search_store_display_name,
            ),
            docs_dir=os.getenv("DOCS_DIR", cls.docs_dir),
            state_path=os.getenv("STATE_PATH", cls.state_path),
            upload_log_path=os.getenv("UPLOAD_LOG_PATH", cls.upload_log_path),
        )
