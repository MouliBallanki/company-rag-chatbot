EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE    = 512
CHUNK_OVERLAP = 100   # increased from 50; reduces context loss at section boundaries

CHROMA_PATH     = "./chroma_db"
COLLECTION_NAME = "rag_docs"

TOP_K = 5

# ChromaDB cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite.
# Results with distance above this threshold are considered irrelevant and dropped.
# Tune lower (e.g. 0.4) for stricter matching, higher (e.g. 0.6) for broader recall.
MAX_DISTANCE_THRESHOLD = 0.5
