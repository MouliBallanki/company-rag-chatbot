# Swapping to a Different LLM Provider

This project currently uses a local Ollama model (`services/llm_service.py::LLMService`)
for answer generation. This note covers both switching Ollama models and swapping
to an entirely different provider (OpenAI, Anthropic, Azure, etc.).

## Option A — Different model, same Ollama backend (trivial)

`LLMService` already takes `model` as a constructor param, defaulting to
`config.OLLAMA_MODEL` (`services/llm_service.py:39`). No code changes needed:

1. Pull the model:
   ```bash
   ollama pull mistral
   ```
2. Edit `config.py`:
   ```python
   OLLAMA_MODEL = "mistral"
   ```

Done — `retrieve.py` picks it up automatically.

## Option B — A different provider entirely (moderate effort)

`ResponseService` has no Ollama-specific knowledge. It only calls:

```python
self._llm.generate(query, answer_context) -> str
```

and catches `LLMServiceError` (`services/response_service.py:65-72`). This is a
duck-typed contract, not an enforced interface/ABC — any object with a matching
`generate()` method works.

### Steps

1. **Create a new service** alongside `LLMService`, e.g. `services/openai_service.py`:
   - `__init__(self, model, api_key, ...)` — store config, build the provider's client.
     Construction should not make a network call (matches `LLMService`'s pattern).
   - `generate(self, query: str, context: list[dict]) -> str`:
     - `context` is the same list of dicts `ResponseService` builds as `answer_context`:
       `{"rank": int, "text": str, "distance": float, "source": str}`.
     - Build a grounded prompt the same way `LLMService._build_prompt` does — reuse
       the same system prompt rules (answer only from context, cite sources, return
       the fixed fallback sentence when context is insufficient).
     - Call the provider's API.
     - Return the generated text.

2. **Raise `LLMServiceError` on failure** — import it from `services.llm_service`
   and raise it (don't invent a new exception type). `ResponseService` only catches
   `LLMServiceError`; anything else will propagate and crash the CLI, breaking the
   "never fail because the LLM backend is unavailable" guarantee described in the
   README.

3. **Wire it in** — in `retrieve.py::build_pipeline`, swap:
   ```python
   llm = LLMService() if use_llm else None
   ```
   for the new service class.

4. **Update `services/__init__.py`** to export the new class if you want it
   importable the same way as the others.

### Gotchas

- `config.py`'s `LLM_PROVIDER = "ollama"` field is currently **decorative only** —
  nothing in the code branches on it. There is no factory/switch that picks a
  provider based on this value. If config-driven provider selection is desired
  (instead of manually editing the `LLMService()` call in `retrieve.py`), that
  factory needs to be built separately.
- Keep the same fallback behavior: `generate()` should return the fixed
  "I don't have enough information..." sentence directly (no network call) when
  `context` is empty, matching `LLMService.generate` (`services/llm_service.py:65-66`).
- `LLM_MAX_CONTEXT_CHUNKS` / `LLM_TIMEOUT` in `config.py` are provider-agnostic
  settings worth reusing rather than duplicating.

### Estimated effort

~30-60 minutes for a straightforward REST-based provider (OpenAI-compatible APIs
are the easiest — the `openai` Python SDK's `chat.completions.create` call is a
near drop-in replacement for `ollama.Client.chat`).
