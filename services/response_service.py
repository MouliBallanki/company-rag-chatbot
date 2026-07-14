import os

from services.llm_service import LLMService, LLMServiceError


class ResponseService:
    """
    Formats vector search results into a structured response, optionally
    enriched with an LLM-generated natural-language answer.

    LLM generation is optional: pass `llm=None` (the default) to run in
    pure-retrieval mode with no LLM call at all (useful for tests, CI, or
    environments without Ollama installed). When an `LLMService` is
    injected but the call fails (Ollama not running, model error, etc.),
    the failure is logged and swallowed — `answer` degrades to `None`
    while `answer_context`/`sources` are still returned intact. The CLI
    must never crash because the LLM backend is unavailable.
    """

    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm

    def build(self, query: str, results: list[dict]) -> dict:
        """
        Build a response from retrieved chunks.

        Returns:
            {
                "query": str,
                "answer": str | None,
                "answer_context": [{"rank": int, "text": str, "distance": float, "source": str}],
                "sources": [str],
            }
        """
        if not results:
            return {
                "query": query,
                "answer": None,
                "answer_context": [],
                "sources": [],
                "message": "No relevant documents found.",
            }

        answer_context = [
            {
                "rank":     idx + 1,
                "text":     r["text"],
                "distance": r["distance"],
                "source":   os.path.basename(r["source"]),
            }
            for idx, r in enumerate(results)
        ]

        unique_sources = sorted({os.path.basename(r["source"]) for r in results})

        answer = self._generate_answer(query, answer_context)

        return {
            "query":          query,
            "answer":         answer,
            "answer_context": answer_context,
            "sources":        unique_sources,
        }

    def _generate_answer(self, query: str, answer_context: list[dict]) -> str | None:
        if self._llm is None:
            return None
        try:
            return self._llm.generate(query, answer_context)
        except LLMServiceError as e:
            print(f"[ResponseService] LLM generation failed, falling back to raw context: {e}")
            return None
