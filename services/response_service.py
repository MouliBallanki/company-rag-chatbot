import os


class ResponseService:
    """
    Formats vector search results into a structured response.

    This is the LLM extension point: replace the body of `build()` with
    an LLM call (OpenAI, Ollama, HuggingFace, etc.) that receives the
    retrieved context and returns a generated answer.
    """

    def build(self, query: str, results: list[dict]) -> dict:
        """
        Build a response from retrieved chunks.

        Returns:
            {
                "query": str,
                "answer_context": [{"rank": int, "text": str, "distance": float}],
                "sources": [str],
            }
        """
        if not results:
            return {
                "query": query,
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

        return {
            "query":          query,
            "answer_context": answer_context,
            "sources":        unique_sources,
        }
