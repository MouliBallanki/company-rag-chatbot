# Generation Pipeline — Remaining Work

LLM answer generation (`services/llm_service.py` + `services/response_service.py` +
`retrieve.py --no-llm`) has been implemented but never executed in this environment
(no `uv`/`pip`/dependencies were available). This checklist covers what's left to
verify it actually works end-to-end.

## Environment setup (required first)
- [ ] Install `uv` — `pip install uv` or the PowerShell installer from astral.sh (README §0)
- [ ] Run `uv sync` — installs all deps including the newly-added `ollama` package and refreshes `uv.lock` (`pyproject.toml`/`requirements.txt` were hand-edited; the lock file still needs regenerating)
- [ ] Install Ollama itself (the application, not just the Python client) from [ollama.com](https://ollama.com)
- [ ] Pull a model — `ollama pull llama3` (or update `OLLAMA_MODEL` in `config.py` for a different/smaller model)
- [ ] Start the Ollama server if it isn't already running as a background service (`ollama serve`, or it may auto-start)

## Verification
- [ ] Run the test suite — `uv run pytest tests/ -v --cov=services --cov=retrieval --cov-report=term-missing`; fix anything that fails (`test_llm_service.py`/`test_response_service.py` were written but never run)
- [ ] Ingest a sample doc — `uv run python ingest.py --file data/documents/<something>.pdf` (or `--dir`) to populate ChromaDB with real content
- [ ] End-to-end query — `uv run python retrieve.py --query "<something in the doc>"`; confirm a generated "Answer:" section appears above the raw chunks and reads as coherent/grounded
- [ ] Graceful-degradation check — stop Ollama (or don't run it) and re-run the same query; confirm it prints raw context with the "no generated answer available" note instead of crashing
- [ ] `--no-llm` check — `uv run python retrieve.py --query "..." --no-llm`; confirm pure-retrieval mode still works unchanged

## Polish (optional)
- [ ] Tune the prompt/system message in `services/llm_service.py` if answers are too verbose, too cautious, or miscite sources
- [ ] Consider pinning `OLLAMA_MODEL` to something smaller/faster (e.g. `phi3`, `qwen2.5:3b`) if `llama3` is too slow on your hardware
- [ ] Commit the changes once verified
