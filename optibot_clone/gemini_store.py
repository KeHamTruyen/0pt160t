from pathlib import Path
import time
from typing import Any

from google import genai


class GeminiKnowledgeStore:
    """Manages a Gemini File Search Store for support docs."""

    def __init__(
        self,
        api_key: str,
        embedding_model: str,
        store_name: str = "",
        store_display_name: str = "optibot-support-docs",
    ) -> None:
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = embedding_model
        self.store_name = store_name
        self.store_display_name = store_display_name

    def ensure_store(self) -> str:
        if self.store_name:
            return self.store_name

        store = self.client.file_search_stores.create(
            config={
                "display_name": self.store_display_name,
                "embedding_model": self.embedding_model,
            }
        )
        self.store_name = store.name
        return self.store_name

    def upload_to_file_search_store(self, path: Path) -> dict[str, Any]:
        store_name = self.ensure_store()
        operation = self.client.file_search_stores.upload_to_file_search_store(
            file_search_store_name=store_name,
            file=str(path),
            config={"display_name": path.name, "mime_type": "text/markdown"},
        )

        while not operation.done:
            time.sleep(5)
            operation = self.client.operations.get(operation)

        if getattr(operation, "error", None):
            raise RuntimeError(f"File Search import failed for {path}: {operation.error}")

        response = getattr(operation, "response", None)
        return {
            "file_search_store_name": store_name,
            "operation_name": getattr(operation, "name", None),
            "document": getattr(response, "name", None) if response else None,
            "display_name": path.name,
        }
