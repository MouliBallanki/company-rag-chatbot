import config
from services import EmbeddingService, VectorService, ResponseService


class RetrievalPipeline:
    """
    Orchestrates the full retrieval flow:
        EmbeddingService -> VectorService -> ResponseService
    """

    def __init__(
        self,
        embedder: EmbeddingService,
        vector_store: VectorService,
        responder: ResponseService,
        top_k: int = config.TOP_K,
    ):
        self._embedder = embedder
        self._vector_store = vector_store
        self._responder = responder
        self._top_k = top_k

    def run(self, query: str) -> dict:
        """
        Run the retrieval pipeline for a user query.

        Returns a structured response dict from ResponseService.
        """
        if not query.strip():
            return {"query": query, "answer_context": [], "sources": [], "message": "Empty query."}

        print(f"\n[RetrievalPipeline] Query: {query!r}")

        query_embedding = self._embedder.encode([query])[0]
        results = self._vector_store.search(query_embedding, top_k=self._top_k)

        print(f"[RetrievalPipeline] Found {len(results)} matching chunk(s).")

        return self._responder.build(query, results)
