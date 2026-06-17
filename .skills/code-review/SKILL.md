---
name: code-review
description: >-
  Review any code change in this project for correctness, security, best
  practices, and test coverage. Use this skill before finalising any
  new feature, bug fix, or refactor.
---

# Code Review

Run this checklist on every meaningful code change before it is considered done.

## How to Use

1. Read the changed files
2. Work through each section below in order
3. Flag every issue as: `BLOCKER` (must fix), `WARNING` (should fix), or `NOTE` (consider)
4. Report findings grouped by file

---

## Section 1 — Correctness

- [ ] Does the code do what the docstring / plan says it does?
- [ ] Are all edge cases handled? (empty input, single item, large input, None)
- [ ] Are return types consistent with the type hints?
- [ ] Is there any off-by-one error in chunk indexing or result slicing?
- [ ] Does the pipeline call services in the right order?
- [ ] Are ChromaDB results correctly unpacked (document, metadata, distance per result)?

## Section 2 — Security

Run the security skill mentally:
- [ ] No file path passed directly to `open()` without validation
- [ ] No secrets in source files (search for `sk-`, `key=`, `password`, `token`)
- [ ] User-supplied query is stripped and length-capped before use
- [ ] No arbitrary collection names from user input
- [ ] `.env` exists in `.gitignore`

## Section 3 — Best Practices

- [ ] All public methods have type hints
- [ ] No bare `except:` clauses
- [ ] No global mutable state
- [ ] Dependencies injected via constructor, not instantiated inside methods
- [ ] Model loaded once in `__init__`, not per call
- [ ] Batch encoding used (not per-item loops)
- [ ] No redundant comments that restate the code
- [ ] Naming follows `snake_case` for methods, `PascalCase` for classes

## Section 4 — Tests

- [ ] There is at least one test for the changed code
- [ ] Happy path is covered
- [ ] At least one edge case (empty input) is covered
- [ ] Real model / real ChromaDB is NOT used in unit tests (mocked)
- [ ] Test function names follow `test_<method>_<scenario>` format
- [ ] No test imports are missing

## Section 5 — Documentation

- [ ] If a public method signature changed → `sync-docs` skill was applied
- [ ] If a config key changed → README config table is updated
- [ ] If a CLI flag changed → README and plan.md CLI sections are updated
- [ ] Docstrings exist on all changed public classes and methods

## Section 6 — Performance

- [ ] Embedding encode is called once per batch, not once per chunk
- [ ] Parser does not load the entire file into memory unnecessarily
- [ ] No N+1 queries to ChromaDB (search once, not per chunk)

---

## Review Report Template

When reporting findings, use this format:

```
## Code Review — <filename>

### BLOCKERS
- [line X] <issue> — <why it matters> — <suggested fix>

### WARNINGS
- [line X] <issue> — <suggested fix>

### NOTES
- [line X] <observation>

### Summary
<one sentence overall assessment>
```

---

## Common Issues in This Project

| Issue | Where It Appears | Fix |
|---|---|---|
| Re-loading embedding model per call | `embedding_service.py` | Move `SentenceTransformer()` to `__init__` |
| Silencing parser errors | `ingestion/pipeline.py` | Log and re-raise, don't swallow |
| Missing `chunk_index` in metadata | `chunker_service.py` | Always include in returned dict |
| Query not stripped before embed | `retrieval/pipeline.py` | `query.strip()` before encoding |
| Hardcoded `"rag_docs"` collection name | anywhere | Always read from `config.COLLECTION_NAME` |
