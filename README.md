# 0PT160T OptiBot Mini-Clone

Python ingestion job for the OptiSigns take-home test. It scrapes at least 30 public Help Center articles, converts them to Markdown, imports changed files into a Gemini File Search Store, and writes a run log.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.sample .env
```

Set `GEMINI_API_KEY` in `.env`.

## Run Locally

```bash
python main.py
```

Docker one-shot job:

```bash
docker build -t 0pt160t .
docker run --rm -e GEMINI_API_KEY=YOUR_KEY 0pt160t
```

Outputs:

- Markdown articles: `data/docs/*.md`
- Delta state: `data/state/articles.json`
- Last run log: `data/logs/last_run.json`
- Gemini File Search Store name: stored in `data/state/articles.json`

Test the assistant from the indexed docs:

```bash
python ask.py "How do I add a YouTube video?"
```

## Gemini Knowledge Approach

This project uses Gemini's managed File Search Store, the Gemini equivalent for managed RAG:

- changed Markdown files are uploaded with `upload_to_file_search_store`;
- Gemini imports, chunks, embeds, and indexes the documents inside the File Search Store;
- unchanged articles are skipped by SHA-256 hash;
- `REQUIRED_ARTICLE_IDS` includes the YouTube article used by the sanity check;
- local chunk counts use Markdown headings plus `CHUNK_SIZE` / `CHUNK_OVERLAP` to explain and log the ingestion size.

The run log records `added`, `updated`, `skipped`, `files_uploaded`, `chunks_indexed`, and `file_search_store_name`.

## Assistant Prompt

```text
You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
```

## Daily Job

This repo includes a GitHub Actions scheduled job in `.github/workflows/daily-ingest.yml`.

Setup:

1. Push the repo to GitHub.
2. Add repository secret `GEMINI_API_KEY`.
3. Open Actions > Daily OptiBot Ingest > Run workflow to test manually.
4. The workflow also runs daily at `07:00 UTC`.

The job re-scrapes, hashes Markdown content, imports only new/updated docs into the Gemini File Search Store, uploads `last_run.json` as an artifact, and commits `data/docs`, `data/state/articles.json`, and `data/logs/last_run.json` so the next scheduled run can detect deltas.

Alternative Render deployment is described by `render.yaml`; set `GEMINI_API_KEY` in Render before running the cron job.

Daily job logs: GitHub Actions > Daily OptiBot Ingest > latest run artifact `optibot-last-run`.

Last local run artifact: `data/logs/last_run.json`

## Screenshot

Add the AI Studio screenshot for: "How do I add a YouTube video?"

Screenshot: TODO
