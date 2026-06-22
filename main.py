"""Drill 10 — Typed Retrieval Endpoint.

Build a FastAPI service with a single `/retrieve` POST endpoint that
returns a top-k token-overlap retrieval against an in-memory fixture,
plus a `/healthz` liveness probe.

The drill teaches the typed-boundary contract: Pydantic request and
response models, OpenAPI documentation at `/docs`, and `Field(...)`
constraints that produce 422 at the boundary rather than 500 inside
the function body.
"""
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from retrieval import retrieve_top_k  # pre-implemented; do not modify retrieval.py

app = FastAPI(title="Drill 10 — Typed Retrieval Endpoint")


# --- Pydantic shapes -------------------------------------------------

class RetrieveRequest(BaseModel):
    """Request body for POST /retrieve.

    Inputs:
        query — non-empty search string (1..500 chars).
        k — number of chunks to return (1..10, default 3).
    """
    # TODO: declare `query: str` with a Field(..., min_length=..., max_length=...)
    #       constraint and `k: int` with ge=... and le=... and a default.
    pass


class Chunk(BaseModel):
    """One retrieved chunk."""
    # TODO: declare chunk_id (int), text (str), score (float).
    pass


class RetrieveResponse(BaseModel):
    """Response body for POST /retrieve."""
    # TODO: declare `retrieved: List[Chunk]`.
    pass


class HealthResponse(BaseModel):
    """Response body for GET /healthz."""
    # TODO: declare `status: str`.
    pass


# --- Path operations -------------------------------------------------

@app.post("/retrieve")
def retrieve(req: RetrieveRequest):
    """Retrieve top-k chunks for a query.

    Returns RetrieveResponse with the top-k token-overlap matches. If no
    chunk overlaps, returns 200 with `retrieved=[]` (not an error).
    """
    # TODO: set response_model=RetrieveResponse on the decorator above,
    #       call retrieve_top_k(req.query, req.k) (imported above from
    #       retrieval.py), and wrap the returned list in a RetrieveResponse.
    raise NotImplementedError


@app.get("/healthz")
def healthz():
    """Liveness probe. Returns 200 with {"status": "ok"}."""
    # TODO: annotate response_model=HealthResponse on the decorator above
    #       and return a HealthResponse.
    raise NotImplementedError
