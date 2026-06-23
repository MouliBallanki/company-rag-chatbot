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

### 2. Add your documents
Drop your `.pdf`, `.docx`, or `.txt` files into:
```
data/documents/
```

### 3. Ingest documents
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

### 4. Query
```bash
uv run python retrieve.py --query "What is the refund policy?"
```
Control how many results come back:
```bash
uv run python retrieve.py --query "Summarize the document" --top-k 3
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
│   └── response_service.py    # ResponseService   (LLM extension point)
├── ingestion/
│   ├── parser.py              # LangChain-based loader (PDF, DOCX, CSV, HTML, text…)
│   └── pipeline.py            # IngestionPipeline — walks full directory tree
├── retrieval/
│   └── pipeline.py            # RetrievalPipeline (with distance threshold filter)
├── tests/
│   ├── conftest.py            # ML library stubs + shared fixtures
│   ├── test_chunker_service.py
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

## Adding an LLM
Open `services/response_service.py` and update `ResponseService.build()` to pass
`answer_context` to your LLM of choice (OpenAI, Ollama, HuggingFace, etc.).

## Running Tests
```bash
uv run pytest tests/ -v
```
