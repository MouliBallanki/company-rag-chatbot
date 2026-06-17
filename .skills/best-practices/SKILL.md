---
name: best-practices
description: >-
  Enforce Python and RAG-specific best practices. Use this skill when writing
  any new code, refactoring existing code, or reviewing a service, pipeline,
  parser, or entry point in this project.
---

# Best Practices

## Python Code Standards

### Type Hints
All public methods must have full type annotations. No `Any` unless unavoidable.

```python
# BAD
def encode(self, texts):
    ...

# GOOD
def encode(self, texts: list[str]) -> list[list[float]]:
    ...
```

### Class Design
- One responsibility per class — services do one thing
- Constructor validates and assigns; it does not compute or call external services beyond initialisation
- Use `__slots__` only when performance profiling shows it's needed — avoid premature optimisation
- No global mutable state; pass dependencies via constructor (dependency injection)

```python
# BAD — service creates its own dependencies
class RetrievalPipeline:
    def __init__(self):
        self.embedder = EmbeddingService()  # hidden coupling

# GOOD — dependencies injected
class RetrievalPipeline:
    def __init__(self, embedder: EmbeddingService, vector_store: VectorService, ...):
        self._embedder = embedder
```

### Error Handling
- Never silence exceptions with bare `except:`
- Raise specific exceptions with context — not just `Exception("something went wrong")`
- Use `try/except` at the pipeline level, not inside every low-level method

```python
# BAD
try:
    result = parser.parse(path)
except:
    pass

# GOOD
try:
    result = parser.parse(path)
except ValueError as e:
    print(f"[IngestionPipeline] Skipping {path}: {e}")
except Exception as e:
    raise RuntimeError(f"Unexpected error parsing {path}") from e
```

### Naming
- Classes: `PascalCase`
- Methods and variables: `snake_case`
- Private attributes: prefix with `_` (e.g. `self._model`)
- Constants in `config.py`: `UPPER_SNAKE_CASE`
- No abbreviations in public APIs (`emb` → `embedding`, `vec` → `vector`)

### Imports
- Standard library first, then third-party, then local
- Absolute imports only — no relative `from . import ...` in service files
- Never import `*`

## RAG-Specific Practices

### Chunking
- Always attach `source` and `chunk_index` metadata to every chunk
- Validate that chunks are non-empty before embedding
- Log the chunk count per document — unexpected zero chunks signals a parser failure

### Embeddings
- Load the model once (in `__init__`) — never reload per call
- Batch encode when possible: `encode(list_of_texts)` not one-by-one
- Normalise embeddings if using cosine similarity manually (ChromaDB handles this internally)

### Vector Store
- Use `upsert` semantics where possible to avoid duplicates on re-ingestion
- Always set `hnsw:space: cosine` explicitly — do not rely on defaults
- Keep `chroma_db/` out of version control (add to `.gitignore`)

### Performance
- The embedding model is the bottleneck — batch all chunks from a file in one `encode()` call
- For large directories, show progress (chunk count per file, total at the end)
- Never load the full document text into a list of characters — use streaming where the parser supports it

## Code Comments

- Comments explain **why**, not **what**
- No comments that restate the code (`# encode the texts`)
- Use docstrings on every public class and method

```python
# BAD
# encode texts
vectors = self._model.encode(texts)

# GOOD
# sentence-transformers returns numpy arrays; .tolist() converts for ChromaDB JSON serialisation
vectors = self._model.encode(texts, convert_to_numpy=True).tolist()
```

## Commit Hygiene

- One logical change per commit
- Commit message: `<type>: <short description>` (e.g. `feat: add docx parser`, `fix: handle empty pdf pages`)
- Never commit: `.env`, `chroma_db/`, `__pycache__/`, `.venv/`
