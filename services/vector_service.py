import uuid
import chromadb
import config


class VectorService:
    """Wraps ChromaDB for persistent vector storage and cosine similarity search."""

    def __init__(self, chroma_path: str = config.CHROMA_PATH, collection_name: str = config.COLLECTION_NAME):
        print(f"[VectorService] Connecting to ChromaDB at: {chroma_path}")
        self._client = chromadb.PersistentClient(path=chroma_path)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        """Upsert chunks and their embeddings into the vector store."""
        if not chunks:
            return

        ids        = [str(uuid.uuid4()) for _ in chunks]
        documents  = [c["text"] for c in chunks]
        metadatas  = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

        self._collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        print(f"[VectorService] Stored {len(chunks)} chunks.")

    def search(self, query_embedding: list[float], top_k: int = config.TOP_K) -> list[dict]:
        """
        Find the top-K most similar chunks.

        Returns a list of dicts:
            { "text": str, "source": str, "chunk_index": int, "distance": float }
        """
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append({
                "text":        doc,
                "source":      meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", -1),
                "distance":    round(dist, 4),
            })
        return hits

    @property
    def count(self) -> int:
        return self._collection.count()
