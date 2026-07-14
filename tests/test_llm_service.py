"""Tests for LLMService — prompt construction, error handling, no-network-at-init."""

import pytest
from unittest.mock import MagicMock, patch

import ollama

from services.llm_service import LLMService, LLMServiceError


# ---------------------------------------------------------------------------
# Helpers and fixtures
# ---------------------------------------------------------------------------

def _context(count: int = 2) -> list[dict]:
    return [
        {"rank": i + 1, "text": f"chunk {i}", "distance": 0.1 * i, "source": f"doc{i}.pdf"}
        for i in range(count)
    ]


@pytest.fixture()
def mock_client() -> MagicMock:
    client = MagicMock()
    client.chat.return_value = {"message": {"content": "  Answer with (Source: doc0.pdf)  "}}
    return client


@pytest.fixture()
def llm_service(mock_client: MagicMock) -> LLMService:
    with patch("services.llm_service.ollama.Client", return_value=mock_client):
        return LLMService(model="llama3", base_url="http://localhost:11434", timeout=60, max_context_chunks=5)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLLMService:
    def test_generate_happy_path_returns_stripped_content(
        self, llm_service: LLMService, mock_client: MagicMock
    ) -> None:
        answer = llm_service.generate("what is the policy?", _context())
        assert answer == "Answer with (Source: doc0.pdf)"

    def test_generate_calls_chat_with_system_and_user_messages(
        self, llm_service: LLMService, mock_client: MagicMock
    ) -> None:
        llm_service.generate("what is the policy?", _context())
        _, kwargs = mock_client.chat.call_args
        assert kwargs["model"] == "llama3"
        roles = [m["role"] for m in kwargs["messages"]]
        assert roles == ["system", "user"]
        user_content = kwargs["messages"][1]["content"]
        assert "what is the policy?" in user_content
        assert "doc0.pdf" in user_content

    def test_generate_empty_context_returns_fallback_without_network_call(
        self, llm_service: LLMService, mock_client: MagicMock
    ) -> None:
        answer = llm_service.generate("anything", [])
        assert "don't have enough information" in answer
        mock_client.chat.assert_not_called()

    def test_generate_respects_max_context_chunks(self, mock_client: MagicMock) -> None:
        with patch("services.llm_service.ollama.Client", return_value=mock_client):
            service = LLMService(max_context_chunks=1)
        service.generate("query", _context(3))
        _, kwargs = mock_client.chat.call_args
        user_content = kwargs["messages"][1]["content"]
        assert "doc0.pdf" in user_content
        assert "doc1.pdf" not in user_content
        assert "doc2.pdf" not in user_content

    def test_generate_response_error_raises_llm_service_error(
        self, llm_service: LLMService, mock_client: MagicMock
    ) -> None:
        mock_client.chat.side_effect = ollama.ResponseError("model not found")
        with pytest.raises(LLMServiceError) as exc_info:
            llm_service.generate("query", _context())
        assert exc_info.value.__cause__ is not None

    def test_generate_connection_error_raises_llm_service_error(
        self, llm_service: LLMService, mock_client: MagicMock
    ) -> None:
        mock_client.chat.side_effect = ConnectionError("refused")
        with pytest.raises(LLMServiceError, match="Could not reach Ollama"):
            llm_service.generate("query", _context())

    def test_init_does_not_call_chat(self, mock_client: MagicMock) -> None:
        with patch("services.llm_service.ollama.Client", return_value=mock_client):
            LLMService()
        mock_client.chat.assert_not_called()
