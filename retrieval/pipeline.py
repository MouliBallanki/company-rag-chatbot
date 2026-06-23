import config
from services import EmbeddingService, VectorService, ResponseService


class RetrievalPipeline:
    """
    Orchestrates the full retrieval flow:
        EmbeddingService -> VectorService -> (threshold filter) -> ResponseService

    Results whose cosine distance exceeds `max_distance` are silently dropped
    so that unrelated queries receive "No relevant documents found." instead of
    hallucinated low-quality context.
    """

    def __init__(
        self,
        embedder: EmbeddingService,
        vector_store: VectorService,
        responder: ResponseService,
        top_k: int = config.TOP_K,
        max_distance: float = config.MAX_DISTANCE_THRESHOLD,
    ) -> None:
        self._embedder = embedder
        self._vector_store = vector_store
        self._responder = responder
        self._top_k = top_k
        self._max_distance = max_distance

    def run(self, query: str) -> dict:
        """
        Run the retrieval pipeline for a user query.

        Returns a structured response dict from ResponseService.
        Chunks with cosine distance > max_distance are excluded from the response.
        """
        if not query.strip():
            return {"query": query, "answer_context": [], "sources": [], "message": "Empty query."}

        print(f"\n[RetrievalPipeline] Query: {query!r}")

        query_embedding = self._embedder.encode([query])[0]
        raw_results = self._vector_store.search(query_embedding, top_k=self._top_k)

        results = [r for r in raw_results if r["distance"] <= self._max_distance]

        dropped = len(raw_results) - len(results)
        if dropped:
            print(f"[RetrievalPipeline] Dropped {dropped} chunk(s) above distance threshold ({self._max_distance}).")

        print(f"[RetrievalPipeline] Found {len(results)} relevant chunk(s).")

        return self._responder.build(query, results)
