"""Tests for ResponseService — context formatting and optional LLM answer generation."""

import pytest
from unittest.mock import MagicMock

from services.response_service import ResponseService
from services.llm_service import LLMServiceError


def _results() -> list[dict]:
    return [
        {"text": "chunk A", "source": "/data/a.pdf", "chunk_index": 0, "distance": 0.1},
        {"text": "chunk B", "source": "/data/b.pdf", "chunk_index": 1, "distance": 0.3},
    ]


@pytest.fixture()
def mock_llm() -> MagicMock:
    llm = MagicMock()
    llm.generate.return_value = "Generated answer (Source: a.pdf)."
    return llm


class TestResponseService:
    def test_build_without_llm_returns_answer_none(self) -> None:
        service = ResponseService()
        response = service.build("query", _results())
        assert response["answer"] is None
        assert len(response["answer_context"]) == 2
        assert response["sources"] == ["a.pdf", "b.pdf"]

    def test_build_with_llm_returns_generated_answer(self, mock_llm: MagicMock) -> None:
        service = ResponseService(llm=mock_llm)
        response = service.build("query", _results())
        assert response["answer"] == mock_llm.generate.return_value
        mock_llm.generate.assert_called_once_with("query", response["answer_context"])

    def test_build_no_results_does_not_call_llm(self, mock_llm: MagicMock) -> None:
        service = ResponseService(llm=mock_llm)
        response = service.build("query", [])
        mock_llm.generate.assert_not_called()
        assert response["answer"] is None
        assert "message" in response

    def test_build_llm_failure_degrades_gracefully(self, mock_llm: MagicMock) -> None:
        mock_llm.generate.side_effect = LLMServiceError("connection refused")
        service = ResponseService(llm=mock_llm)
        response = service.build("query", _results())
        assert response["answer"] is None
        assert len(response["answer_context"]) == 2
        assert response["sources"] == ["a.pdf", "b.pdf"]

    def test_response_service_returns_ranked_context(self) -> None:
        service = ResponseService()
        response = service.build("query", _results())
        assert response["answer_context"][0]["rank"] == 1
        assert response["answer_context"][1]["rank"] == 2

    def test_response_service_no_results(self) -> None:
        service = ResponseService()
        response = service.build("query", [])
        assert response["answer_context"] == []
        assert response["sources"] == []
        assert "No relevant documents found." == response["message"]
