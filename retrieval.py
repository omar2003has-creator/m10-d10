"""Pre-implemented retrieval over a fixed in-memory fixture.

DO NOT MODIFY. The drill exercises FastAPI endpoint authoring and
Pydantic model validation; the retrieval logic is provided so you focus
on the request/response surface.

Scoring is simple token overlap: count the unique query tokens that
appear in the chunk text (case-insensitive). Ties broken by lower
``chunk_id`` first.
"""
from __future__ import annotations


_FIXTURE_CHUNKS: list[dict] = [
    {"chunk_id": 1, "text": "FastAPI is a modern Python web framework built on Starlette and Pydantic."},
    {"chunk_id": 2, "text": "Pydantic models validate request and response bodies and produce OpenAPI schemas."},
    {"chunk_id": 3, "text": "Uvicorn is the ASGI server that FastAPI runs under in development and production."},
    {"chunk_id": 4, "text": "Retrieval-augmented generation pulls top-k chunks and grounds the model output in citations."},
    {"chunk_id": 5, "text": "Docker Compose composes multi-service stacks with healthchecks and dependency ordering."},
]


def _tokens(text: str) -> set[str]:
    return {tok.lower().strip(".,") for tok in text.split() if tok}


def retrieve_top_k(query: str, k: int = 3) -> list[dict]:
    """Return the top-``k`` chunks ranked by token-overlap with ``query``.

    Each returned dict has shape ``{"chunk_id": int, "text": str, "score": float}``.
    ``score`` is the count of unique query tokens that appear in the chunk
    text, divided by the number of unique query tokens (so ``0.0 < score <= 1.0``).
    Zero-score chunks are excluded; a query with no overlap returns ``[]``.
    """
    q_tokens = _tokens(query)
    denom = max(len(q_tokens), 1)
    scored: list[dict] = []
    for chunk in _FIXTURE_CHUNKS:
        c_tokens = _tokens(chunk["text"])
        overlap = len(q_tokens & c_tokens)
        if overlap == 0:
            continue
        scored.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "score": overlap / denom,
        })
    scored.sort(key=lambda r: (-r["score"], r["chunk_id"]))
    return scored[:k]
