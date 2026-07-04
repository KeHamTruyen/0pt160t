from optibot_clone.config import Settings
from optibot_clone.pipeline import run_pipeline


def main() -> None:
    settings = Settings.from_env()
    result = run_pipeline(settings)
    print(
        "Run complete: "
        f"added={result['added']} updated={result['updated']} "
        f"skipped={result['skipped']} files_uploaded={result['files_uploaded']} "
        f"chunks_indexed={result['chunks_indexed']} "
        f"file_search_store={result['file_search_store_name']}"
    )


if __name__ == "__main__":
    main()
