"""Drill 10 autograder.

Per the Autograder Test Path Rule, `..` (not `../starter/`) is the
correct insertion. In a learner's accepted repo, `main.py` lives at the
repo root; `tests/` is a sibling directory. The starter/ directory only
exists in this staging layout.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app  # noqa: E402

client = TestClient(app)


# ----- /healthz ------------------------------------------------------

def test_healthz_returns_ok():
    """Catches buggy variant: learner forgets HealthResponse model and
    returns a bare string."""
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert body.get("status") == "ok"


def test_healthz_uses_response_model():
    """Catches buggy variant: learner returns extra fields not declared
    on HealthResponse (response_model filters them)."""
    r = client.get("/healthz")
    assert set(r.json().keys()) == {"status"}


# ----- /retrieve happy path ------------------------------------------

def test_retrieve_returns_response_shape():
    """Catches buggy variant: learner returns a bare list instead of a
    RetrieveResponse wrapping `retrieved`."""
    r = client.post("/retrieve", json={"query": "fastapi pydantic", "k": 3})
    assert r.status_code == 200
    body = r.json()
    assert "retrieved" in body
    assert isinstance(body["retrieved"], list)


def test_retrieve_chunk_fields_present():
    """Catches buggy variant: learner returns chunks missing the `score`
    field, or names it differently."""
    r = client.post("/retrieve", json={"query": "fastapi", "k": 3})
    assert r.status_code == 200
    for c in r.json()["retrieved"]:
        assert set(c.keys()) == {"chunk_id", "text", "score"}
        assert isinstance(c["chunk_id"], int)
        assert isinstance(c["text"], str)
        assert isinstance(c["score"], float)


def test_retrieve_orders_by_score_descending():
    """Catches buggy variant: learner returns chunks in fixture order, OR
    returns an empty list (in which case sorted([]) == [] vacuously passes
    an ordering check that does not require at least one result first)."""
    r = client.post(
        "/retrieve",
        json={"query": "compose healthchecks docker", "k": 3},
    )
    assert r.status_code == 200
    scores = [c["score"] for c in r.json()["retrieved"]]
    assert len(scores) >= 1, (
        "Query 'compose healthchecks docker' should overlap at least one "
        "fixture chunk; empty result indicates retrieve_top_k was not "
        "called or returned [] incorrectly."
    )
    assert scores == sorted(scores, reverse=True)


def test_retrieve_respects_k():
    """Catches buggy variant: learner ignores `k` and returns all matches."""
    r = client.post("/retrieve", json={"query": "the", "k": 2})
    assert r.status_code == 200
    assert len(r.json()["retrieved"]) == 2


def test_retrieve_default_k_is_three():
    """Catches buggy variant: learner declares `k: int` without a default,
    or learner ignores k and returns more than 3 chunks."""
    r = client.post("/retrieve", json={"query": "a is the"})
    # 200, not 422, means the default was applied.
    assert r.status_code == 200
    retrieved = r.json()["retrieved"]
    # Default k=3 means at most 3 chunks, each with the Chunk shape.
    assert len(retrieved) <= 3
    for c in retrieved:
        assert set(c.keys()) == {"chunk_id", "text", "score"}


# ----- /retrieve zero matches ----------------------------------------

def test_retrieve_zero_matches_returns_200_empty():
    """Catches buggy variant: learner raises 404/500 when no chunk
    overlaps the query."""
    r = client.post(
        "/retrieve",
        json={"query": "zzzzzz quoxotic blurbleflarp", "k": 3},
    )
    assert r.status_code == 200
    assert r.json()["retrieved"] == []


# ----- /retrieve validation gates ------------------------------------

def _assert_happy_path_accepted():
    """Control: a valid body must produce 200, so we know the 422 we see
    on bad bodies came from the Field constraint, not from an unannotated
    `req` parameter rejecting every body at the boundary."""
    r = client.post("/retrieve", json={"query": "fastapi", "k": 3})
    assert r.status_code == 200, (
        "Valid request body must return 200; got "
        f"{r.status_code}. If 422, the `req` parameter is likely "
        "missing the RetrieveRequest annotation."
    )


def test_retrieve_empty_query_rejected():
    """Catches buggy variant: learner writes `query: str` instead of
    `Field(..., min_length=1)`. Empty string falls through to the body
    and produces an internal error or empty result."""
    _assert_happy_path_accepted()
    r = client.post("/retrieve", json={"query": "", "k": 3})
    assert r.status_code == 422


def test_retrieve_oversized_query_rejected():
    """Catches buggy variant: learner omits max_length and ships an
    open-ended query field."""
    _assert_happy_path_accepted()
    r = client.post("/retrieve", json={"query": "x" * 501, "k": 3})
    assert r.status_code == 422


def test_retrieve_k_out_of_range_rejected_low():
    """Catches buggy variant: learner uses `k: int = 3` without ge=1."""
    _assert_happy_path_accepted()
    r = client.post("/retrieve", json={"query": "fastapi", "k": 0})
    assert r.status_code == 422


def test_retrieve_k_out_of_range_rejected_high():
    """Catches buggy variant: learner omits le=10."""
    _assert_happy_path_accepted()
    r = client.post("/retrieve", json={"query": "fastapi", "k": 11})
    assert r.status_code == 422


# ----- OpenAPI schema ------------------------------------------------

def test_openapi_documents_retrieve_endpoint():
    """Catches buggy variant: learner returns a dict from /retrieve
    instead of using response_model=RetrieveResponse, breaking the
    OpenAPI schema."""
    schema = client.get("/openapi.json").json()
    assert "/retrieve" in schema["paths"]
    op = schema["paths"]["/retrieve"]["post"]
    # response_model declared → 200 response references a schema.
    assert "200" in op["responses"]
    # The 200 response must reference RetrieveResponse (or any schema
    # that declares the `retrieved` field). Without response_model the
    # 200 entry is a bare content-less stub.
    content = op["responses"]["200"].get("content", {})
    json_schema = content.get("application/json", {}).get("schema", {})
    ref = json_schema.get("$ref", "")
    if ref:
        # Resolve $ref to a component schema and check field name.
        schema_name = ref.rsplit("/", 1)[-1]
        component = schema["components"]["schemas"].get(schema_name, {})
        assert "retrieved" in component.get("properties", {}), (
            f"OpenAPI 200 schema {schema_name} must declare `retrieved`; "
            "set response_model=RetrieveResponse on the decorator."
        )
    else:
        # Inline schema (no $ref) — must still declare `retrieved`.
        assert "retrieved" in json_schema.get("properties", {}), (
            "OpenAPI 200 schema must declare `retrieved`; set "
            "response_model=RetrieveResponse on the decorator."
        )
