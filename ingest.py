"""
Ingestion entry point.

Usage:
    python ingest.py
    python ingest.py --dir data/documents
    python ingest.py --file data/documents/report.pdf
"""

import argparse
import os
import sys

import config
from services import ChunkerService, EmbeddingService, VectorService
from ingestion.pipeline import IngestionPipeline


def build_pipeline() -> IngestionPipeline:
    chunker     = ChunkerService(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    embedder    = EmbeddingService(config.EMBEDDING_MODEL)
    vector_store = VectorService(config.CHROMA_PATH, config.COLLECTION_NAME)
    return IngestionPipeline(chunker, embedder, vector_store)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG vector store.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dir",  default="data/documents", help="Directory of documents to ingest (default: data/documents)")
    group.add_argument("--file", help="Single file to ingest")
    args = parser.parse_args()

    pipeline = build_pipeline()

    if args.file:
        if not os.path.isfile(args.file):
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)
        pipeline.run_file(args.file)
    else:
        if not os.path.isdir(args.dir):
            print(f"ERROR: Directory not found: {args.dir}")
            print("Create it and add your documents, then re-run.")
            sys.exit(1)
        pipeline.run_directory(args.dir)


if __name__ == "__main__":
    main()
