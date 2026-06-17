# Code Review Examples

Real examples of issues found and how they were fixed in this project.

---

## Example 1 — Model reloaded per call (BLOCKER)

```python
# BAD — model reloaded on every encode() call
class EmbeddingService:
    def encode(self, texts):
        model = SentenceTransformer("all-MiniLM-L6-v2")  # 2-3 seconds each call
        return model.encode(texts).tolist()

# GOOD — model loaded once at init
class EmbeddingService:
    def __init__(self, model_name: str):
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, convert_to_numpy=True).tolist()
```

---

## Example 2 — Bare except silences parser crash (BLOCKER)

```python
# BAD
try:
    text, meta = Parser.parse(file_path)
except:
    text = ""

# GOOD
try:
    text, meta = Parser.parse(file_path)
except ValueError as e:
    print(f"[IngestionPipeline] Skipping {file_path}: {e}")
    return 0
except Exception as e:
    raise RuntimeError(f"Failed to parse {file_path}") from e
```

---

## Example 3 — Missing type hints on public method (WARNING)

```python
# BAD
def chunk(self, text, source):
    ...

# GOOD
def chunk(self, text: str, source: str) -> list[dict]:
    ...
```

---

## Example 4 — Query not validated before embedding (WARNING)

```python
# BAD
def run(self, query):
    embedding = self._embedder.encode([query])[0]

# GOOD
def run(self, query: str) -> dict:
    query = query.strip()
    if not query:
        return {"query": query, "answer_context": [], "sources": [], "message": "Empty query."}
    if len(query) > 2000:
        raise ValueError(f"Query too long ({len(query)} chars). Max 2000.")
    embedding = self._embedder.encode([query])[0]
```
