---
name: security
description: >-
  Enforce security best practices for the RAG pipeline. Use this skill when
  adding new code, handling file uploads, storing data, reading config, or
  exposing any interface to external input.
---

# Security Practices

Apply these rules to every change. Security is not optional.

## 1. File Handling

### Path Traversal Prevention
Never trust a user-supplied file path directly.

```python
# BAD
def parse(file_path: str):
    with open(file_path) as f: ...

# GOOD
import os

ALLOWED_DIR = os.path.abspath("data/documents")

def parse(file_path: str):
    safe_path = os.path.abspath(file_path)
    if not safe_path.startswith(ALLOWED_DIR):
        raise ValueError(f"Access denied: {file_path}")
    with open(safe_path) as f: ...
```

### Allowed File Types
Only process extensions defined in `Parser.SUPPORTED`. Reject everything else before opening the file.

### File Size Limit
Enforce a maximum file size before reading to prevent memory exhaustion:
```python
MAX_FILE_SIZE_MB = 50
if os.path.getsize(path) > MAX_FILE_SIZE_MB * 1024 * 1024:
    raise ValueError(f"File too large: {path}")
```

## 2. Secrets and Configuration

- **Never hardcode** API keys, tokens, passwords, or model endpoints in source files
- Store secrets in environment variables or a `.env` file (not committed to git)
- Use `python-dotenv` to load `.env` — add `.env` to `.gitignore` immediately
- `config.py` must contain only **non-sensitive** defaults

```python
# config.py — safe
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# .env — never commit
OPENAI_API_KEY=sk-...
```

## 3. Input Validation

All external input (CLI args, query strings, file content) must be validated before use:

- Sanitise query strings: strip leading/trailing whitespace, reject empty strings
- Cap query length: `MAX_QUERY_LENGTH = 2000` characters
- Validate `--top-k` is a positive integer within bounds (1–50)
- Validate `--dir` and `--file` paths exist and are within the allowed directory

## 4. Vector Store

- Never expose the raw ChromaDB path to external users
- Do not allow arbitrary collection names from user input — use only `config.COLLECTION_NAME`
- When deleting or resetting the store, require explicit confirmation (not automated)

## 5. Dependency Security

- Pin major versions in `pyproject.toml` to avoid supply-chain surprises
- Run `uv lock` to generate a lockfile; commit `uv.lock` to version control
- Periodically audit dependencies: `uv pip check`

## 6. Logging

- Never log raw document content, query text, or embedding vectors
- Log file names and chunk counts only
- Do not log stack traces to stdout in production — capture them with a logger

## 7. .gitignore Checklist

Ensure these are always in `.gitignore`:
```
.env
chroma_db/
*.pyc
__pycache__/
.venv/
```

## Security Review Checklist

Before any PR or commit:
- [ ] No secrets in source files
- [ ] File paths validated against allowed directory
- [ ] File size checked before reading
- [ ] User input (query, flags) validated and capped
- [ ] `.env` and `chroma_db/` in `.gitignore`
- [ ] No sensitive data logged
