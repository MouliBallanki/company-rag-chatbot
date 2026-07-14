"""
Pytest configuration and shared fixtures.

Heavy ML / vector-store libraries are replaced with lightweight stubs before
any test module imports them. This lets unit tests run without loading real
models, downloading weights, or connecting to ChromaDB.

All stubs use direct assignment (not setdefault) to guarantee the mock is
active even if a library was partially touched during pytest startup.
"""

import sys
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Stub: langchain_text_splitters
# A minimal RecursiveCharacterTextSplitter that actually splits by character
# count so ChunkerService tests exercise real splitting behaviour.
# ---------------------------------------------------------------------------

class _FakeRecursiveCharacterTextSplitter:
    """Minimal drop-in that splits text at chunk_size boundaries with overlap."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
        length_function=None,
        **_kwargs,
    ) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        if not text.strip():
            return []
        if len(text) <= self._chunk_size:
            return [text]
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self._chunk_size, len(text))
            chunks.append(text[start:end])
            next_start = end - self._chunk_overlap
            if next_start <= start:
                break
            start = next_start
        return chunks


_mock_langchain_splitters = MagicMock()
_mock_langchain_splitters.RecursiveCharacterTextSplitter = (
    _FakeRecursiveCharacterTextSplitter
)
sys.modules["langchain_text_splitters"] = _mock_langchain_splitters


# ---------------------------------------------------------------------------
# Stubs: ML and vector-store libraries
# Direct assignment (not setdefault) guarantees the mock wins even if a
# library was partially initialised before this conftest ran.
# ---------------------------------------------------------------------------

for _mod in (
    "sentence_transformers",
    "chromadb",
    "chromadb.config",
    "transformers",
    "huggingface_hub",
):
    sys.modules[_mod] = MagicMock()
