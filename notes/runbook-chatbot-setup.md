# Runbook: Company RAG Chatbot — Full Stack Setup

Covers standing up the whole chatbot (vector store → API → React UI) from a
clean clone on Windows. For CLI-only usage (`ingest.py` / `retrieve.py`) see
`README.md`.

## Components

| Component | Tech | Default address |
|---|---|---|
| Vector store | ChromaDB (persistent, on disk at `chroma_db/`) | n/a |
| LLM backend | Ollama (local) | `http://localhost:11434` |
| API | FastAPI (`api/main.py`) | `http://localhost:8000` |
| Frontend | React + Vite (`rag-ui/`) | `http://localhost:5173` |

The frontend is hardcoded to call the API at `http://localhost:8000/api`
(`rag-ui/src/api.js`). If you run the API on a different port, update that
file too.

## 1. Prerequisites (one-time)

- Python ≥ 3.10
- [`uv`](https://astral.sh/uv) — `pip install uv`
- Node.js + npm (for the Vite/React frontend)
- [Ollama](https://ollama.com) — required for generated answers; without it
  `/api/chat` still responds but `answer` comes back `null` and only raw
  retrieved chunks are returned.

## 2. Backend setup

```bash
cd company-rag-chatbot

# Install Python deps into .venv (reads pyproject.toml)
uv sync

# Pull the local LLM model (matches config.OLLAMA_MODEL)
ollama pull llama3
```

**Known gap:** `uv sync` may not install `fastapi` / `starlette` /
`python-multipart` even though they're listed in `pyproject.toml`, if the
existing `.venv` was created before those deps were added. Symptom:
`ModuleNotFoundError: No module named 'fastapi'` when starting uvicorn.
Fix: re-run `uv sync` — it will diff and install anything missing.

## 3. Ingest documents

Drop files into `data/documents/` (`.pdf`, `.docx`, `.txt`, `.csv`, `.html`,
`.md`, …), then:

```bash
uv run python ingest.py
```

Verify the vector store actually has data before testing the API:

```bash
.venv\Scripts\python.exe -c "import chromadb; c=chromadb.PersistentClient(path='./chroma_db'); print(c.get_or_create_collection('rag_docs').count())"
```

If this prints `0`, `/api/chat` will always return `"No relevant documents
found."` regardless of whether the API/LLM are wired correctly — rule this
out first when debugging "empty answer" reports.

## 4. Start Ollama

Ollama usually runs as a background service after install. Confirm it's
listening:

```bash
curl http://localhost:11434
```

If not running, start it (`ollama serve`, or launch the Ollama app).

## 5. Start the API

```bash
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Port **must** be `8000` to match the frontend's hardcoded `API_BASE_URL`
unless you also edit `rag-ui/src/api.js`.

Cold start takes ~30–90s the first time (loading `sentence-transformers` +
`chromadb`) — the process is done and ready when you see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Sanity check:
```bash
curl -s http://127.0.0.1:8000/docs -o /dev/null -w "%{http_code}\n"   # expect 200
```

## 6. Start the frontend

```bash
cd rag-ui
npm install     # first time only
npm run dev
```

Open `http://localhost:5173`, click the 💬 bubble bottom-right, and chat.

## 7. Verify the integration end-to-end

Bypass the browser and hit the API directly the way the frontend does
(cross-origin, JSON body):

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5173" \
  -d '{"query": "What is the refund policy?"}'
```

Checks to run against the response:
- HTTP 200, and response headers include
  `access-control-allow-origin: http://localhost:5173` (confirms CORS is
  correctly configured for the frontend's origin).
- Body has a non-null `"answer"` field with a `(Source: ...)` citation, for
  a query that matches ingested content.
- A clearly irrelevant query returns
  `"message": "No relevant documents found."` with `"answer": null` instead
  of a crash or hallucinated content.

Then confirm in the browser itself: ask the same question in the chat
drawer and check the rendered answer + the "📌 Sources" line matches.

## 8. Shutting down

- Frontend: `Ctrl+C` in the `npm run dev` terminal (or kill the vite node
  process on port 5173).
- API: `Ctrl+C` in the uvicorn terminal (or kill the process on port 8000).
- Nothing else needs to be torn down — ChromaDB is just files on disk.

## Troubleshooting quick reference

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | `.venv` predates fastapi being added to `pyproject.toml` | `uv sync` |
| `/api/chat` always returns "No relevant documents found." | `chroma_db` collection is empty, or query is genuinely unrelated to ingested docs, or `MAX_DISTANCE_THRESHOLD` in `config.py` is too strict | Check collection count (§3); re-ingest; loosen threshold if needed |
| `"answer": null` but `answer_context` has results | Ollama not running, wrong model pulled, or call timed out | `curl http://localhost:11434`; `ollama pull llama3`; check `LLM_TIMEOUT` in `config.py` |
| Frontend shows `❌ Error connecting to agent` | API not running, wrong port, or CORS misconfigured | Confirm API is up on `:8000`; check `api/main.py` CORS middleware allows the frontend origin |
| Frontend chat renders `[object Object]` | Stale build using old `answer_context.join('\n')` logic against the new structured `answer_context` (list of `{rank, text, distance, source}`) | Already fixed in `rag-ui/src/App.jsx` — pull latest, or rebuild if you see this |
| First API request very slow (30–90s) | Cold model/library load (`sentence-transformers`, `chromadb`) on first pipeline build | Expected — the retrieval pipeline is cached as a singleton after the first request, so subsequent calls are fast |
