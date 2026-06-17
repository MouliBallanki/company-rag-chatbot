# Documentation Map

Maps every documented item to its source-of-truth code location.
Update this file whenever a new item is documented.

## Services

| Documented Item | Code Location | Documented In |
|---|---|---|
| `EmbeddingService.encode()` | `services/embedding_service.py` | `README.md`, `plan.md` |
| `ChunkerService.chunk()` | `services/chunker_service.py` | `README.md`, `plan.md` |
| `VectorService.add()` | `services/vector_service.py` | `README.md`, `plan.md` |
| `VectorService.search()` | `services/vector_service.py` | `README.md`, `plan.md` |
| `ResponseService.build()` | `services/response_service.py` | `README.md`, `plan.md` |

## Config Keys

| Key | Default | Documented In |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | `README.md`, `plan.md`, `config.py` |
| `CHUNK_SIZE` | `512` | `README.md`, `plan.md`, `config.py` |
| `CHUNK_OVERLAP` | `50` | `README.md`, `plan.md`, `config.py` |
| `CHROMA_PATH` | `./chroma_db` | `README.md`, `plan.md`, `config.py` |
| `COLLECTION_NAME` | `rag_docs` | `README.md`, `plan.md`, `config.py` |
| `TOP_K` | `5` | `README.md`, `plan.md`, `config.py` |

## CLI Flags

| Command | Flag | Documented In |
|---|---|---|
| `ingest.py` | `--dir` | `README.md`, `plan.md` |
| `ingest.py` | `--file` | `README.md` |
| `retrieve.py` | `--query` | `README.md`, `plan.md` |
| `retrieve.py` | `--top-k` | `README.md` |
