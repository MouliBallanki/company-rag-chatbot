---
name: testing
description: >-
  Write or update test cases whenever code changes. Use this skill when a
  service method, pipeline step, parser, or CLI entry point is added, modified,
  or fixed. Tests live in tests/ and use pytest.
---

# Testing

Every code change must be covered by a test. No exceptions.

## Setup

Tests use `pytest`. Install once:
```bash
uv add --dev pytest pytest-mock
```

Run all tests:
```bash
uv run pytest tests/ -v
```

Run a single test file:
```bash
uv run pytest tests/test_chunker_service.py -v
```

## Test File Locations

```
tests/
├── conftest.py                  # shared fixtures
├── test_chunker_service.py
├── test_embedding_service.py
├── test_vector_service.py
├── test_response_service.py
├── ingestion/
│   ├── test_parser.py
│   └── test_ingestion_pipeline.py
└── retrieval/
    └── test_retrieval_pipeline.py
```

## What to Test for Each Change

### When a service method changes
Write tests for:
1. **Happy path** — valid input returns correct output
2. **Edge cases** — empty input, single item, maximum size
3. **Error path** — invalid input raises the right exception with a clear message

### When a parser is added or changed
Write tests for:
1. Each supported file type with a real minimal fixture file
2. Empty document returns empty string, not an exception
3. Unsupported extension raises `ValueError`
4. File path outside allowed directory raises `ValueError` (security)

### When a pipeline changes
Write tests for:
1. Full pipeline integration with mocked services (not real model/DB)
2. Verify services are called in the correct order with correct arguments
3. Verify the return value shape matches the contract

### When a CLI flag changes
Write tests for:
1. Flag present with valid value — correct pipeline is called
2. Flag missing — default is used
3. Invalid value — process exits with non-zero code and clear message

## Test Patterns

### Mocking Services (do not load real models in unit tests)
```python
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_embedder():
    embedder = MagicMock()
    embedder.encode.return_value = [[0.1, 0.2, 0.3]]
    return embedder

@pytest.fixture
def mock_vector_store():
    store = MagicMock()
    store.search.return_value = [
        {"text": "sample chunk", "source": "doc.pdf", "chunk_index": 0, "distance": 0.12}
    ]
    return store
```

### Testing a Service Method
```python
def test_chunker_splits_text():
    from services.chunker_service import ChunkerService
    chunker = ChunkerService(chunk_size=100, chunk_overlap=10)
    chunks = chunker.chunk("word " * 50, source="test.txt")
    assert len(chunks) > 1
    for c in chunks:
        assert "text" in c
        assert c["source"] == "test.txt"
        assert isinstance(c["chunk_index"], int)

def test_chunker_empty_text_returns_empty():
    from services.chunker_service import ChunkerService
    chunker = ChunkerService()
    assert chunker.chunk("", source="test.txt") == []
```

### Testing the Response Service
```python
def test_response_service_returns_ranked_context():
    from services.response_service import ResponseService
    rs = ResponseService()
    results = [
        {"text": "chunk A", "source": "/data/a.pdf", "chunk_index": 0, "distance": 0.1},
        {"text": "chunk B", "source": "/data/b.pdf", "chunk_index": 1, "distance": 0.3},
    ]
    response = rs.build("What is X?", results)
    assert response["query"] == "What is X?"
    assert len(response["answer_context"]) == 2
    assert response["answer_context"][0]["rank"] == 1
    assert "a.pdf" in response["sources"]

def test_response_service_no_results():
    from services.response_service import ResponseService
    rs = ResponseService()
    response = rs.build("empty query", [])
    assert response["answer_context"] == []
    assert "message" in response
```

### Testing the Retrieval Pipeline
```python
def test_retrieval_pipeline_calls_services_in_order(mock_embedder, mock_vector_store):
    from services.response_service import ResponseService
    from retrieval.pipeline import RetrievalPipeline

    responder = ResponseService()
    pipeline = RetrievalPipeline(mock_embedder, mock_vector_store, responder, top_k=3)
    response = pipeline.run("test query")

    mock_embedder.encode.assert_called_once_with(["test query"])
    mock_vector_store.search.assert_called_once()
    assert "query" in response
```

## Naming Rules

- Test files: `test_<module_name>.py`
- Test functions: `test_<method>_<scenario>` (e.g. `test_chunk_empty_text_returns_empty`)
- Fixtures: descriptive nouns (e.g. `mock_embedder`, `sample_pdf_path`)

## Coverage Target

Aim for 80%+ coverage on all `services/` and `ingestion/` modules.
Check coverage:
```bash
uv run pytest tests/ --cov=services --cov=ingestion --cov=retrieval --cov-report=term-missing
```
(Requires: `uv add --dev pytest-cov`)
