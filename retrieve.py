"""
Retrieval entry point.

Usage:
    python retrieve.py --query "What is the refund policy?"
    python retrieve.py --query "Summarize the document" --top-k 3
"""

import argparse
import json
import sys

import config
from services import EmbeddingService, VectorService, ResponseService, LLMService
from retrieval.pipeline import RetrievalPipeline


def build_pipeline(top_k: int, use_llm: bool = True) -> RetrievalPipeline:
    embedder     = EmbeddingService(config.EMBEDDING_MODEL)
    vector_store = VectorService(config.CHROMA_PATH, config.COLLECTION_NAME)
    llm          = LLMService() if use_llm else None
    responder    = ResponseService(llm=llm)
    return RetrievalPipeline(embedder, vector_store, responder, top_k=top_k)


def main():
    parser = argparse.ArgumentParser(description="Query the RAG vector store.")
    parser.add_argument("--query",  required=True, help="The question to ask")
    parser.add_argument("--top-k",  type=int, default=config.TOP_K, help=f"Number of results to return (default: {config.TOP_K})")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM answer generation and only return raw retrieved context")
    args = parser.parse_args()

    pipeline = build_pipeline(args.top_k, use_llm=not args.no_llm)
    response = pipeline.run(args.query)

    print("\n" + "=" * 60)
    print(f"Query   : {response['query']}")
    print(f"Sources : {', '.join(response.get('sources', [])) or 'none'}")
    print("=" * 60)

    answer = response.get("answer")
    if answer:
        print("\nAnswer:")
        print("-" * 40)
        print(answer)
    elif response.get("answer_context"):
        print("\n[No generated answer available — showing raw retrieved context below.]")

    for item in response.get("answer_context", []):
        print(f"\n[Rank {item['rank']}] (distance: {item['distance']}) — {item['source']}")
        print("-" * 40)
        print(item["text"])

    if not response.get("answer_context"):
        print(response.get("message", "No results found."))


if __name__ == "__main__":
    main()
