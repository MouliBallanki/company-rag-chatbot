# RAG Design Patterns Reference

## Chunking Strategies

| Strategy | When to Use |
|---|---|
| `RecursiveCharacterTextSplitter` (current) | General documents, balanced quality/speed |
| Sentence splitting | When semantic completeness per chunk matters more than size |
| Paragraph-aware | Structured documents (reports, manuals) — split on double newlines first |
| Sliding window | Dense technical docs where context overlaps are critical |

**Current setting**: `CHUNK_SIZE=512`, `CHUNK_OVERLAP=50`
Tune `CHUNK_SIZE` up for longer-context queries, down for precise fact retrieval.

## Embedding Models (sentence-transformers)

| Model | Dims | Speed | Best For |
|---|---|---|---|
| `all-MiniLM-L6-v2` (current) | 384 | Fast | General retrieval, low resource |
| `all-mpnet-base-v2` | 768 | Medium | Higher accuracy retrieval |
| `multi-qa-MiniLM-L6-cos-v1` | 384 | Fast | Q&A retrieval specifically |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | Medium | Multi-language documents |

## Retrieval Quality Improvements

1. **Re-ranking**: after top-K retrieval, re-score with a cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
2. **Hybrid search**: combine dense (embedding) + sparse (BM25 keyword) retrieval
3. **Metadata filtering**: filter by `source` filename before similarity search for scoped queries
4. **Query expansion**: generate multiple phrasings of the query before embedding

## Vector Store Options

| Store | Type | Best For |
|---|---|---|
| ChromaDB (current) | Local persistent | Development, single-machine |
| FAISS | Local in-memory | High-throughput, large scale |
| Pinecone | Cloud managed | Production, multi-user |
| Qdrant | Self-hosted / cloud | Production with filtering |
