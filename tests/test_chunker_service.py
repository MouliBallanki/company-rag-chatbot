"""Tests for ChunkerService — heading-aware chunking for PDF policy documents."""

import pytest

from services.chunker_service import ChunkerService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def chunker() -> ChunkerService:
    return ChunkerService(chunk_size=200, chunk_overlap=20)


POLICY_TEXT = """\
1. Introduction
This document outlines the company leave policies.
All employees must adhere to the guidelines below.

2. Annual Leave
Employees are entitled to 20 days of annual leave per year.
Leave must be applied at least 5 working days in advance.

3. Sick Leave
Employees may avail up to 10 days of sick leave per year.
A medical certificate is required for absences exceeding 3 days.
"""

NO_HEADING_TEXT = """\
This is a plain paragraph with no headings.
It should still be chunked normally.
The chunker must not crash or return empty results.
"""

ALLCAPS_TEXT = """\
LEAVE ENCASHMENT POLICY
Employees can encash up to 30 days of leave at the time of separation.
The encashment is calculated based on basic pay only.

HR & ADMIN GUIDELINES
All HR requests must be routed through the self-service portal.
"""

COLON_HEADING_TEXT = """\
Policy Overview:
This section provides a high-level summary of all company policies.

Travel Guidelines:
Employees travelling on company business must book through the approved portal.
"""


# ---------------------------------------------------------------------------
# _is_heading tests
# ---------------------------------------------------------------------------

class TestIsHeading:
    def test_numbered_heading_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("1. Introduction") is True

    def test_numbered_subheading_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("4.2 Leave Encashment Policy") is True

    def test_allcaps_heading_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("LEAVE POLICY") is True

    def test_allcaps_with_ampersand_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("HR & ADMIN GUIDELINES") is True

    def test_colon_heading_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("Policy Overview:") is True

    def test_body_sentence_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("Employees are entitled to 20 days of leave.") is False

    def test_line_ending_with_comma_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("As per the policy,") is False

    def test_empty_line_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("") is False

    def test_very_long_line_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("A" * 101) is False

    def test_too_short_line_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("Hi") is False

    # --- Real BBIL SYSTEMS POSH policy document patterns ---

    def test_allcaps_title_with_parentheses_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("POLICY FOR PREVENTION OF SEXUAL HARASSMENT (POSH)") is True

    def test_numbered_allcaps_colon_detected(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("1. PURPOSE:") is True

    def test_numbered_allcaps_scope(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("2. SCOPE:") is True

    def test_numbered_allcaps_applicability(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("3. APPLICABLITY:") is True

    def test_numbered_allcaps_definition(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("4. DEFINITION:") is True

    def test_numbered_allcaps_double_space(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("5.  POLICY GUIDELINES:") is True

    def test_numbered_long_allcaps_inner_colon(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("6. GRIEVANCE MECHANISM: PROCEDURE TO REGISTER COMPLAINTS:") is True

    def test_numbered_allcaps_internal_committee(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("7. INTERNAL COMMITTEE:") is True

    def test_roman_numeral_single_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("I.") is False

    def test_roman_numeral_double_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("II.") is False

    def test_roman_numeral_triple_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("III.") is False

    def test_roman_numeral_four_not_heading(self, chunker: ChunkerService) -> None:
        assert chunker._is_heading("IV.") is False


# ---------------------------------------------------------------------------
# _split_into_sections tests
# ---------------------------------------------------------------------------

class TestSplitIntoSections:
    def test_numbered_headings_produce_correct_sections(self, chunker: ChunkerService) -> None:
        sections = chunker._split_into_sections(POLICY_TEXT)
        headings = [h for h, _ in sections]
        assert "1. Introduction" in headings
        assert "2. Annual Leave" in headings
        assert "3. Sick Leave" in headings

    def test_each_section_body_contains_relevant_text(self, chunker: ChunkerService) -> None:
        sections = dict(chunker._split_into_sections(POLICY_TEXT))
        assert "20 days of annual leave" in sections.get("2. Annual Leave", "")
        assert "sick leave" in sections.get("3. Sick Leave", "")

    def test_no_heading_text_returns_single_section(self, chunker: ChunkerService) -> None:
        sections = chunker._split_into_sections(NO_HEADING_TEXT)
        assert len(sections) == 1
        heading, body = sections[0]
        assert heading == ""
        assert "plain paragraph" in body

    def test_allcaps_headings_detected(self, chunker: ChunkerService) -> None:
        sections = chunker._split_into_sections(ALLCAPS_TEXT)
        headings = [h for h, _ in sections]
        assert "LEAVE ENCASHMENT POLICY" in headings
        assert "HR & ADMIN GUIDELINES" in headings

    def test_colon_headings_detected(self, chunker: ChunkerService) -> None:
        sections = chunker._split_into_sections(COLON_HEADING_TEXT)
        headings = [h for h, _ in sections]
        assert "Policy Overview:" in headings
        assert "Travel Guidelines:" in headings


# ---------------------------------------------------------------------------
# chunk() tests
# ---------------------------------------------------------------------------

class TestChunk:
    def test_empty_text_returns_empty_list(self, chunker: ChunkerService) -> None:
        assert chunker.chunk("", source="doc.pdf") == []

    def test_whitespace_only_returns_empty_list(self, chunker: ChunkerService) -> None:
        assert chunker.chunk("   \n\n  ", source="doc.pdf") == []

    def test_chunk_keys_present(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(POLICY_TEXT, source="policy.pdf")
        assert len(chunks) > 0
        for chunk in chunks:
            assert "text" in chunk
            assert "source" in chunk
            assert "chunk_index" in chunk
            assert "heading" in chunk

    def test_source_preserved_in_all_chunks(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(POLICY_TEXT, source="hr_policy.pdf")
        for chunk in chunks:
            assert chunk["source"] == "hr_policy.pdf"

    def test_chunk_indices_are_sequential(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(POLICY_TEXT, source="doc.pdf")
        indices = [c["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_heading_prepended_to_chunk_text(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(POLICY_TEXT, source="doc.pdf")
        headed_chunks = [c for c in chunks if c["heading"]]
        assert len(headed_chunks) > 0
        for chunk in headed_chunks:
            assert chunk["text"].startswith(f"[Section: {chunk['heading']}]")

    def test_no_heading_chunk_has_empty_heading_field(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(NO_HEADING_TEXT, source="doc.pdf")
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk["heading"] == ""
            assert not chunk["text"].startswith("[Section:")

    def test_no_empty_chunks_returned(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(POLICY_TEXT, source="doc.pdf")
        for chunk in chunks:
            assert chunk["text"].strip() != ""

    def test_multiple_headings_produce_multiple_chunks(self, chunker: ChunkerService) -> None:
        chunks = chunker.chunk(POLICY_TEXT, source="doc.pdf")
        unique_headings = {c["heading"] for c in chunks if c["heading"]}
        assert len(unique_headings) >= 3

    def test_single_short_document_returns_one_chunk(self, chunker: ChunkerService) -> None:
        text = "1. Policy\nThis is the only sentence."
        chunks = chunker.chunk(text, source="short.pdf")
        assert len(chunks) == 1
        assert chunks[0]["chunk_index"] == 0
        assert chunks[0]["heading"] == "1. Policy"
