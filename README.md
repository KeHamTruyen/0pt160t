# 0PT160T

OptiBot mini-clone ingestion job. It scrapes OptiSigns Help Center articles, saves clean Markdown, imports changed docs into a Gemini File Search Store, and logs added/updated/skipped counts.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.sample .env
```

Set `GEMINI_API_KEY` in `.env`. Do not commit `.env`.

## Run

```bash
python main.py
python ask.py "How do I add a YouTube video?"
```

Docker one-shot job:

```bash
docker build -t 0pt160t .
docker run --rm -e API_KEY=YOUR_GEMINI_KEY 0pt160t
```

Outputs:

- Markdown docs: `data/docs/*.md`
- Delta state and File Search Store name: `data/state/articles.json`
- Last run artifact: `data/logs/last_run.json`

## Ingestion

- Pulls 30 latest articles from `support.optisigns.com` plus required sanity-check article `360051014713`.
- Converts article HTML to Markdown while preserving headings, code blocks, and links.
- Detects deltas with SHA-256 content hashes.
- Uploads only new/updated Markdown files with Gemini `upload_to_file_search_store`.
- Gemini File Search Store handles managed RAG indexing; local chunk counts use Markdown headings plus `CHUNK_SIZE` / `CHUNK_OVERLAP`.

Latest local run: `added=0 updated=0 skipped=31 files_uploaded=0 chunks_indexed=0`.

## Assistant

System prompt:

```text
You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
```

Sample screenshot:

![Assistant answer with citation](<Screenshot 2026-07-04 151401.png>)

## Daily Job

GitHub Actions workflow: `.github/workflows/daily-ingest.yml`.

Setup:

1. Push this repo to GitHub.
2. Add repository secret `GEMINI_API_KEY`.
3. Run `Actions > Daily OptiBot Ingest > Run workflow`.
4. The schedule runs daily at `07:00 UTC`.

Daily job logs/artifact: GitHub Actions > Daily OptiBot Ingest > latest run > artifact `optibot-last-run`.

Optional Render cron deployment is included in `render.yaml`.
