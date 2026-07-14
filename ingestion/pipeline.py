import os
from ingestion.parser import Parser
from services import ChunkerService, EmbeddingService, VectorService


# Directories to never recurse into, regardless of location in the tree.
_SKIP_DIRS: frozenset[str] = frozenset({
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    "chroma_db", ".skills", ".cursor",
})


class IngestionPipeline:
    """
    Orchestrates the full ingestion flow:
        Parser -> ChunkerService -> EmbeddingService -> VectorService
    """

    def __init__(
        self,
        chunker: ChunkerService,
        embedder: EmbeddingService, 
        vector_store: VectorService,
    ):
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store

    def run_file(self, file_path: str) -> int:
        """
        Ingest a single file. Returns the number of chunks stored.
        Skips binary/non-text files silently.
        """
        if Parser.is_skippable(file_path):
            print(f"  -> Skipped (binary or excluded): {os.path.basename(file_path)}")
            return 0

        print(f"\n[IngestionPipeline] Processing: {os.path.basename(file_path)}")

        try:
            text, meta = Parser.parse(file_path)
        except Exception as e:
            print(f"  -> Parse error, skipping: {e}")
            return 0

        if not text.strip():
            print("  -> Empty content, skipping.")
            return 0

        chunks = self._chunker.chunk(text, source=file_path)
        print(f"  -> {len(chunks)} chunks created.")

        if not chunks:
            return 0

        embeddings = self._embedder.encode([c["text"] for c in chunks])
        self._vector_store.add(chunks, embeddings)

        return len(chunks)

    def run_directory(self, directory: str) -> dict:
        """
        Recursively ingest ALL readable files in a directory tree.

        Skips:
          - Hidden files and dotfiles (names starting with '.')
          - Known binary extensions (images, audio, compiled, archives, etc.)
          - Specific filenames (.gitkeep, .gitignore, uv.lock, etc.)
          - Directories: .git, __pycache__, .venv, chroma_db, .skills, etc.

        Returns a summary dict: { file_path: chunks_stored }
        """
        summary: dict[str, int] = {}
        collected: list[str] = []

        for root, dirs, files in os.walk(directory):
            # Prune directories in-place so os.walk won't descend into them.
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]

            for filename in files:
                file_path = os.path.join(root, filename)
                if not Parser.is_skippable(file_path):
                    collected.append(file_path)

        if not collected:
            print(f"[IngestionPipeline] No readable files found in: {directory}")
            return summary

        print(f"[IngestionPipeline] Found {len(collected)} file(s) to ingest.")

        skipped = 0
        for file_path in collected:
            try:
                n = self.run_file(file_path)
                summary[file_path] = n
                if n == 0:
                    skipped += 1
            except Exception as e:
                print(f"  -> ERROR processing {file_path}: {e}")
                summary[file_path] = 0
                skipped += 1

        ingested = len(collected) - skipped
        total_chunks = sum(summary.values())
        print(
            f"\n[IngestionPipeline] Done. "
            f"{ingested}/{len(collected)} file(s) ingested, "
            f"{total_chunks} total chunks stored."
        )
        return summary
