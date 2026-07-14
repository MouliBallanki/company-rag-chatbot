import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

# Matches heading-like lines commonly found in company policy PDFs:
#   "1. PURPOSE:", "4.2 Leave Policy", "10.3.1 Sub-clause"          → numbered
#   "LEAVE POLICY", "HR & ADMIN GUIDELINES"                         → ALL CAPS
#   "POLICY FOR PREVENTION OF SEXUAL HARASSMENT (POSH)"             → ALL CAPS with parens
#   "6. GRIEVANCE MECHANISM: PROCEDURE TO REGISTER COMPLAINTS:"     → numbered long ALL CAPS
#   "Policy Overview:", "Travel Guidelines:"                        → Title case ending in colon
_HEADING_RE = re.compile(
    r"^(?:"
    r"\d+(?:\.\d+)*\.?\s+[A-Z\w]"          # numbered: "1. PURPOSE:", "4.2 Policy Name"
    r"|[A-Z][A-Z0-9\s\-/&:,()\[\]]{3,}$"   # ALL CAPS: "LEAVE POLICY", "POSH (POLICY)"
    r"|[A-Z][a-zA-Z0-9\s]{2,60}:\s*$"      # Title with colon: "Policy Overview:"
    r")"
)


class ChunkerService:
    """
    Splits raw text into overlapping chunks with source and heading metadata.

    For PDF and DOCX policy documents, headings are detected by regex and
    prepended to every chunk so the LLM always knows which section it is reading.
    """

    def __init__(
        self,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def _is_heading(self, line: str) -> bool:
        """Return True if the line looks like a section heading."""
        stripped = line.strip()
        if len(stripped) < 3 or len(stripped) > 100:
            return False
        if stripped.endswith((".", ",", ";", "?")):
            return False
        return bool(_HEADING_RE.match(stripped))

    def _split_into_sections(self, text: str) -> list[tuple[str, str]]:
        """
        Partition text into (heading, body) pairs.

        If the document starts before any detected heading, that block is stored
        with an empty heading string.
        """
        sections: list[tuple[str, str]] = []
        current_heading: str = ""
        body_lines: list[str] = []

        for line in text.splitlines():
            if self._is_heading(line):
                if body_lines:
                    sections.append((current_heading, "\n".join(body_lines)))
                    body_lines = []
                current_heading = line.strip()
            else:
                body_lines.append(line)

        if body_lines:
            sections.append((current_heading, "\n".join(body_lines)))

        return sections if sections else [("", text)]

    def chunk(self, text: str, source: str) -> list[dict]:
        """
        Split text into chunks, prepending the detected section heading to each.

        Returns a list of dicts:
            {
                "text":        str,   # "[Section: <heading>]\\n<body>" or just body
                "source":      str,
                "chunk_index": int,
                "heading":     str,   # empty string if no heading was detected
            }
        """
        if not text.strip():
            return []

        sections = self._split_into_sections(text)
        all_chunks: list[dict] = []
        global_idx: int = 0

        for heading, body in sections:
            if not body.strip():
                continue

            pieces = self._splitter.split_text(body)
            for piece in pieces:
                chunk_text = f"[Section: {heading}]\n{piece}" if heading else piece
                all_chunks.append(
                    {
                        "text": chunk_text,
                        "source": source,
                        "chunk_index": global_idx,
                        "heading": heading,
                    }
                )
                global_idx += 1

        return all_chunks
