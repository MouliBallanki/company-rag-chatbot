# Chatbot RAG

A service-oriented Retrieval-Augmented Generation (RAG) pipeline.

## Quick Start

### 0. Install uv (once, if not already installed)
```bash
pip install uv
```
Or via the official installer on Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 1. Install dependencies
```bash
uv sync
```
This reads `pyproject.toml`, creates a virtual environment automatically, and installs all packages.

### 2. Install Ollama and pull a model (for generated answers)
Download Ollama from [ollama.com](https://ollama.com), then pull the default model:
```bash
ollama pull llama3
```
Ollama runs its own local server at `http://localhost:11434` (matches `OLLAMA_BASE_URL` in `config.py`) — no API key required. If you skip this step, `retrieve.py` still works and falls back to returning raw retrieved context (see "LLM Answer Generation" below).

### 3. Add your documents
Drop your `.pdf`, `.docx`, or `.txt` files into:
```
data/documents/
```

### 4. Ingest documents
```bash
uv run python ingest.py
```
Or point to a specific folder:
```bash
uv run python ingest.py --dir data/documents
```
Or ingest a single file:
```bash
uv run python ingest.py --file data/documents/report.pdf
```

### 5. Query
```bash
uv run python retrieve.py --query "What is the refund policy?"
```
Control how many results come back:
```bash
uv run python retrieve.py --query "Summarize the document" --top-k 3
```
Skip LLM answer generation and only return raw retrieved context (no Ollama required):
```bash
uv run python retrieve.py --query "What is the refund policy?" --no-llm
```

### Adding a new package later
```bash
uv add <package-name>
```

## Project Structure
```
Chatbot_RAG/
├── services/
│   ├── embedding_service.py   # EmbeddingService  (sentence-transformers)
│   ├── chunker_service.py     # ChunkerService    (heading-aware PDF chunking)
│   ├── vector_service.py      # VectorService     (ChromaDB)
│   ├── llm_service.py         # LLMService        (Ollama local LLM)
│   └── response_service.py    # ResponseService   (formats context + calls LLM)
├── ingestion/
│   ├── parser.py              # LangChain-based loader (PDF, DOCX, CSV, HTML, text…)
│   └── pipeline.py            # IngestionPipeline — walks full directory tree
├── retrieval/
│   └── pipeline.py            # RetrievalPipeline (with distance threshold filter)
├── tests/
│   ├── conftest.py            # ML library stubs + shared fixtures
│   ├── test_chunker_service.py
│   ├── test_llm_service.py
│   ├── test_response_service.py
│   └── retrieval/
│       └── test_retrieval_pipeline.py
├── data/documents/            # <-- put your files here (any readable file type)
├── chroma_db/                 # auto-created vector store
├── config.py                  # all settings
├── ingest.py                  # ingestion CLI
└── retrieve.py                # retrieval CLI
```

## Supported File Types

| Extension | Loader |
|---|---|
| `.pdf` | `PyMuPDFLoader` |
| `.docx` | `Docx2txtLoader` |
| `.csv` | `CSVLoader` |
| `.html` / `.htm` | `BSHTMLLoader` |
| `.txt`, `.md`, `.json`, `.yaml`, `.py`, `.rst`, `.xml` … | `TextLoader` |

Binary files (images, audio, video, archives, compiled) are auto-skipped.

## Configuration
Edit `config.py` to tune:
| Setting | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformer model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks (increased for policy docs) |
| `TOP_K` | `5` | Results returned per query |
| `MAX_DISTANCE_THRESHOLD` | `0.5` | Cosine distance cutoff — results above this are dropped as irrelevant |
| `LLM_PROVIDER` | `ollama` | LLM backend identifier |
| `OLLAMA_MODEL` | `llama3` | Ollama model used for answer generation |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_TIMEOUT` | `60` | Seconds to wait for an Ollama response |
| `LLM_MAX_CONTEXT_CHUNKS` | `TOP_K` | Ranked chunks fed into the LLM prompt |

## LLM Answer Generation
`retrieve.py` generates a grounded natural-language answer via a local Ollama model (`services/llm_service.py::LLMService`), injected into `ResponseService`. The model is instructed to answer only from the retrieved context and cite sources.

- Pass `--no-llm` to skip generation and only return raw retrieved context.
- If Ollama isn't running or the model call fails, `retrieve.py` degrades gracefully: `response["answer"]` is `None` and the raw ranked context is still printed — the CLI never crashes because the LLM backend is unavailable.
- To use a different provider, implement a new service alongside `LLMService` (e.g. `OpenAIService`) and inject it into `ResponseService` instead.

## Running Tests
```bash
uv run pytest tests/ -v
```
