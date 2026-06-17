# Threat Model — Chatbot RAG

## Assets

| Asset | Sensitivity | Location |
|---|---|---|
| Document contents | High — may contain confidential HR/legal data | `data/documents/`, `chroma_db/` |
| Embedding vectors | Medium — derived from document content | `chroma_db/` |
| User queries | Medium — reveals user intent | In memory only |
| API keys (future LLM) | Critical | `.env` |

## Threat Scenarios

### T1 — Path Traversal
**Vector**: `--file` or `--dir` CLI argument points outside `data/documents/`
**Impact**: Arbitrary file read, potential exfiltration of system files
**Mitigation**: `os.path.abspath` + prefix check against `ALLOWED_DIR`

### T2 — Malicious PDF / DOCX
**Vector**: Crafted document triggers parser vulnerability (e.g. PyMuPDF exploit)
**Impact**: Code execution, memory corruption
**Mitigation**: File size limit, keep PyMuPDF updated, never execute document content

### T3 — Secret Leakage via Git
**Vector**: `.env` or `chroma_db/` accidentally committed
**Impact**: API key exposure, document content exposure
**Mitigation**: `.gitignore`, pre-commit hook to scan for secrets

### T4 — Query Injection (future LLM)
**Vector**: User crafts a query to override system prompt
**Impact**: Prompt injection, data exfiltration via LLM
**Mitigation**: Sanitise query before passing to LLM, use system prompt pinning

### T5 — Dependency Compromise
**Vector**: Malicious version of `chromadb`, `sentence-transformers`, etc.
**Impact**: Supply-chain attack
**Mitigation**: Commit `uv.lock`, audit on updates
