from langchain_text_splitters import RecursiveCharacterTextSplitter
import config


class ChunkerService:
    """Splits raw text into overlapping chunks with source metadata."""

    def __init__(self, chunk_size: int = config.CHUNK_SIZE, chunk_overlap: int = config.CHUNK_OVERLAP):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def chunk(self, text: str, source: str) -> list[dict]:
        """
        Split text into chunks.

        Returns a list of dicts:
            { "text": str, "source": str, "chunk_index": int }
        """
        if not text.strip():
            return []

        pieces = self._splitter.split_text(text)
        return [
            {"text": piece, "source": source, "chunk_index": idx}
            for idx, piece in enumerate(pieces)
        ]
