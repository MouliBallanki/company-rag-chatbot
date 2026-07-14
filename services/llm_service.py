import ollama

import config


class LLMServiceError(RuntimeError):
    """Raised when the Ollama backend is unreachable or returns an error."""


class LLMService:
    """
    Generates a grounded natural-language answer from ranked retrieval
    context using a local Ollama model.

    Construction only stores configuration and builds a lightweight HTTP
    client wrapper — it performs no network call. The first network call
    happens in `generate()`.
    """

    _SYSTEM_PROMPT = (
        "You are a helpful assistant that answers questions using ONLY the "
        "context excerpts provided below, which come from internal company "
        "documents. Follow these rules strictly:\n"
        "1. Answer using only information found in the CONTEXT section.\n"
        "2. Never use outside knowledge or make assumptions beyond the context.\n"
        "3. When you state a fact, cite its source in parentheses, e.g. (Source: policy.pdf).\n"
        "4. If the context does not contain enough information to answer the "
        "question confidently, respond with exactly this sentence and nothing else: "
        "\"I don't have enough information in the provided documents to answer this confidently.\"\n"
        "5. Be concise and directly address the question."
    )

    _FALLBACK_ANSWER = (
        "I don't have enough information in the provided documents to answer this confidently."
    )

    def __init__(
        self,
        model: str = config.OLLAMA_MODEL,
        base_url: str = config.OLLAMA_BASE_URL,
        timeout: int = config.LLM_TIMEOUT,
        max_context_chunks: int = config.LLM_MAX_CONTEXT_CHUNKS,
    ) -> None:
        self._model = model
        self._base_url = base_url
        self._timeout = timeout
        self._max_context_chunks = max_context_chunks
        self._client = ollama.Client(host=base_url, timeout=timeout)

    def generate(self, query: str, context: list[dict]) -> str:
        """
        Build a grounded prompt from ranked context chunks and return the
        model's generated answer text.

        `context` items are the same dicts ResponseService builds as
        `answer_context`: { "rank", "text", "distance", "source" }.

        Returns the fallback "not enough information" sentence directly
        (without a network call) if `context` is empty.

        Raises:
            LLMServiceError: if Ollama returns an error response or the
                server cannot be reached (connection refused, timeout, etc.).
        """
        if not context:
            return self._FALLBACK_ANSWER

        prompt = self._build_prompt(query, context)
        try:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.2},
            )
        except ollama.ResponseError as e:
            raise LLMServiceError(
                f"Ollama model error (model={self._model!r} at {self._base_url}): {e}"
            ) from e
        except Exception as e:
            raise LLMServiceError(
                f"Could not reach Ollama at {self._base_url} (model={self._model!r}): {e}"
            ) from e

        return response["message"]["content"].strip()

    def _build_prompt(self, query: str, context: list[dict]) -> str:
        limited = context[: self._max_context_chunks]
        formatted_chunks = "\n\n---\n\n".join(
            f"[Source: {c['source']} | rank {c['rank']} | distance {c['distance']}]\n{c['text']}"
            for c in limited
        )
        return f"CONTEXT:\n{formatted_chunks}\n\nQUESTION:\n{query}\n\nANSWER:"
