"""Tests for RetrievalPipeline — distance threshold filtering."""

import pytest
from unittest.mock import MagicMock

from retrieval.pipeline import RetrievalPipeline
from services.response_service import ResponseService


# ---------------------------------------------------------------------------
# Helpers and fixtures
# ---------------------------------------------------------------------------

def _make_result(distance: float, source: str = "doc.pdf") -> dict:
    return {
        "text": f"sample chunk at distance {distance}",
        "source": source,
        "chunk_index": 0,
        "distance": distance,
    }


@pytest.fixture()
def mock_embedder() -> MagicMock:
    embedder = MagicMock()
    embedder.encode.return_value = [[0.1, 0.2, 0.3]]
    return embedder


@pytest.fixture()
def mock_vector_store() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def responder() -> ResponseService:
    return ResponseService()


def _make_pipeline(
    mock_embedder: MagicMock,
    mock_vector_store: MagicMock,
    responder: ResponseService,
    max_distance: float = 0.5,
) -> RetrievalPipeline:
    return RetrievalPipeline(
        embedder=mock_embedder,
        vector_store=mock_vector_store,
        responder=responder,
        top_k=5,
        max_distance=max_distance,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDistanceThreshold:
    def test_results_within_threshold_are_returned(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [_make_result(0.2), _make_result(0.4)]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("what is the leave policy?")
        assert len(response["answer_context"]) == 2

    def test_results_above_threshold_are_dropped(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [
            _make_result(0.3),
            _make_result(0.8),
            _make_result(0.9),
        ]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("leave policy")
        assert len(response["answer_context"]) == 1
        assert response["answer_context"][0]["distance"] == 0.3

    def test_all_results_above_threshold_returns_no_results_message(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [
            _make_result(0.7),
            _make_result(0.8992),   # the "world war" scenario
        ]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("what is world war")
        assert response["answer_context"] == []
        assert "message" in response
        assert "No relevant" in response["message"]

    def test_result_exactly_at_threshold_is_included(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [_make_result(0.5)]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("policy query")
        assert len(response["answer_context"]) == 1

    def test_empty_store_returns_no_results_message(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = []
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("any query")
        assert response["answer_context"] == []
        assert "message" in response

    def test_empty_query_short_circuits_before_search(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("   ")
        mock_embedder.encode.assert_not_called()
        mock_vector_store.search.assert_not_called()
        assert "message" in response

    def test_sources_only_contain_passing_results(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [
            _make_result(0.2, source="/data/policy.pdf"),
            _make_result(0.9, source="/data/unrelated.pdf"),
        ]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("policy question")
        assert "policy.pdf" in response["sources"]
        assert "unrelated.pdf" not in response["sources"]

    def test_custom_strict_threshold(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [
            _make_result(0.25),
            _make_result(0.35),
        ]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder, max_distance=0.3)
        response = pipeline.run("query")
        assert len(response["answer_context"]) == 1
        assert response["answer_context"][0]["distance"] == 0.25

    def test_embedder_called_once_per_query(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [_make_result(0.2)]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        pipeline.run("test query")
        mock_embedder.encode.assert_called_once_with(["test query"])


class TestLLMIntegration:
    def test_pipeline_includes_generated_answer_when_llm_injected(
        self, mock_embedder, mock_vector_store
    ) -> None:
        mock_vector_store.search.return_value = [_make_result(0.2)]
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "The leave policy allows 20 days (Source: doc.pdf)."
        responder = ResponseService(llm=mock_llm)
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)

        response = pipeline.run("what is the leave policy?")

        assert response["answer"] == mock_llm.generate.return_value
        mock_llm.generate.assert_called_once()

    def test_pipeline_without_llm_has_answer_key_none(
        self, mock_embedder, mock_vector_store, responder
    ) -> None:
        mock_vector_store.search.return_value = [_make_result(0.2)]
        pipeline = _make_pipeline(mock_embedder, mock_vector_store, responder)
        response = pipeline.run("query")
        assert response["answer"] is None
