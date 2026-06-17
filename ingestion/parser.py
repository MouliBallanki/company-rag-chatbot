import os

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    BSHTMLLoader,
    TextLoader,
)


class Parser:
    """
    Routes any file to the correct LangChain document loader.

    - .pdf          → PyMuPDFLoader   (page-by-page extraction)
    - .docx         → Docx2txtLoader
    - .csv          → CSVLoader       (each row becomes a document)
    - .html / .htm  → BSHTMLLoader    (strips HTML tags)
    - everything else readable → TextLoader  (.txt, .md, .json, .yaml, .py, .rst, .xml …)
    - known binaries / dotfiles / excluded names → skipped via is_skippable()
    """

    BINARY_EXTENSIONS: frozenset[str] = frozenset({
        # images
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp", ".tiff",
        # audio / video
        ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flac", ".ogg", ".webm",
        # compiled / native
        ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin", ".obj",
        # archives
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
        # ML / data blobs
        ".pkl", ".npy", ".npz", ".h5", ".hdf5", ".parquet", ".feather", ".arrow",
        # databases
        ".db", ".sqlite", ".sqlite3",
        # fonts
        ".ttf", ".otf", ".woff", ".woff2",
    })

    SKIP_FILENAMES: frozenset[str] = frozenset({
        ".gitkeep", ".gitignore", ".gitattributes", ".dockerignore",
        ".env", ".env.example", "uv.lock", "poetry.lock", "package-lock.json",
        "Thumbs.db", ".DS_Store",
    })

    # Extension → LangChain loader class
    _LOADER_MAP: dict = {
        ".pdf":  PyMuPDFLoader,
        ".docx": Docx2txtLoader,
        ".csv":  CSVLoader,
        ".html": BSHTMLLoader,
        ".htm":  BSHTMLLoader,
    }

    @classmethod
    def is_binary(cls, file_path: str) -> bool:
        """Return True if the file extension is a known binary format."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.BINARY_EXTENSIONS

    @classmethod
    def is_skippable(cls, file_path: str) -> bool:
        """Return True if the file should not be ingested."""
        name = os.path.basename(file_path)
        if name.startswith(".") or name in cls.SKIP_FILENAMES:
            return True
        return cls.is_binary(file_path)

    @classmethod
    def parse(cls, file_path: str) -> tuple[str, dict]:
        """
        Load a file with the appropriate LangChain loader and return
        (raw_text, metadata).

        Metadata dict:
            { "source": str, "file_type": str, "pages": int | None }

        All LangChain Document objects from the loader are joined with
        double newlines into a single text string.
        """
        ext = os.path.splitext(file_path)[1].lower()
        loader_cls = cls._LOADER_MAP.get(ext)

        if loader_cls is None:
            # Universal fallback for .txt, .md, .json, .yaml, .py, .rst, .xml …
            loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
        elif ext == ".csv":
            loader = CSVLoader(file_path, encoding="utf-8")
        else:
            loader = loader_cls(file_path)

        docs = loader.load()
        text = "\n\n".join(doc.page_content for doc in docs if doc.page_content.strip())

        pages = len(docs) if ext == ".pdf" else None
        file_type = ext.lstrip(".") or "txt"

        return text, {"source": file_path, "file_type": file_type, "pages": pages}
