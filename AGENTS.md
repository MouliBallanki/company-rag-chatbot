# Agent Instructions — Chatbot RAG

You are an AI developer working on a service-oriented RAG pipeline.
Follow these instructions on every prompt, without being asked.

---

## 1. Skill System

All skills live in `.skills/`. Read `.skills/SKILLS.md` first for the full index.
Each skill has a `SKILL.md` — read and follow it completely before proceeding.
Also read any files in that skill's `references/` folder when relevant.

---

## 2. Automatic Skill Application

Apply skills based on what is changing, not just what the user asks.
Multiple skills apply simultaneously for most changes. Apply them in this order:

### On ANY code change (new feature, fix, refactor):
1. Read `.skills/best-practices/SKILL.md` — follow all Python and RAG coding standards while writing
2. Read `.skills/security/SKILL.md` — check the security rules apply to the change
3. Read `.skills/testing/SKILL.md` — write or update tests in `tests/` for the changed code
4. Read `.skills/sync-docs/SKILL.md` — update README.md and plan.md if any public interface, config key, CLI flag, or folder structure changed
5. Read `.skills/code-review/SKILL.md` — run the review checklist before declaring the change done; report any BLOCKERs and fix them before finishing

### On a review or refactor request only:
- Focus on `.skills/code-review/SKILL.md` — produce a structured report using the report template

### On a security question or threat discussion:
- Focus on `.skills/security/SKILL.md` and `.skills/security/references/threat-model.md`

### On a documentation task:
- Focus on `.skills/sync-docs/SKILL.md` and `.skills/sync-docs/references/doc-map.md`

### On a testing task:
- Focus on `.skills/testing/SKILL.md` — write tests following the patterns defined there

---

## 3. Project Rules

- **Services** (`services/`) are independent classes. Each has one responsibility. Dependencies are injected via constructor — never instantiated inside a method.
- **Pipelines** (`ingestion/pipeline.py`, `retrieval/pipeline.py`) are thin orchestrators — they call services in sequence, nothing else.
- **Config** (`config.py`) is the single source of truth for all settings. Never hardcode values that belong in config.
- **No secrets in source files** — use environment variables loaded via `python-dotenv`.
- **Tests live in `tests/`** and use `pytest`. Unit tests must mock services — never load the real embedding model or real ChromaDB in unit tests.
- **Package manager is `uv`** — use `uv add`, `uv sync`, `uv run`. Never use bare `pip install`.

---

## 4. File Ownership

| Directory / File | Responsibility |
|---|---|
| `services/` | One service class per file. Each class is self-contained. |
| `ingestion/parser.py` | Routes file types to parsers. Returns `(text, metadata)`. |
| `ingestion/pipeline.py` | Orchestrates: parse → chunk → embed → store |
| `retrieval/pipeline.py` | Orchestrates: embed query → search → build response |
| `config.py` | All tuneable settings. No logic. |
| `ingest.py` | CLI entry point for ingestion only |
| `retrieve.py` | CLI entry point for retrieval only |
| `tests/` | All test files. Mirror the source structure. |
| `.skills/` | Agent skill definitions. Do not modify unless asked. |
| `data/documents/` | Raw input documents. Never commit real documents to git. |
| `chroma_db/` | Auto-generated. Never commit. Always in `.gitignore`. |

---

## 5. Before Finishing Any Task

Run through this quick checklist mentally before your final response:

- [ ] Does the code follow best-practices (type hints, no bare except, DI)?
- [ ] Are security rules satisfied (no path traversal, no secrets, input validated)?
- [ ] Are tests written or updated?
- [ ] Is documentation in sync (README, plan.md)?
- [ ] Does the code-review checklist pass (no BLOCKERs)?

If any item fails, fix it before responding.

---

## 6. Response Format for Code Changes

After every code change, end your response with a short summary block:

```
## Changes made
- <file>: <what changed and why>

## Tests
- <test file>: <what is covered>

## Docs updated
- <file>: <what section changed>  OR  "No public interface changed — no doc update needed"
```

This is mandatory. Never finish a code-change response without this block.
