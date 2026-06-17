from sentence_transformers import SentenceTransformer
import config


class EmbeddingService:
    """Loads the embedding model once and encodes text into vectors."""

    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        print(f"[EmbeddingService] Loading model: {model_name}")
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode a list of strings into embedding vectors."""
        if not texts:
            return []
        vectors = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return vectors.tolist()
