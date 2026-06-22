from fastapi import FastAPI
from pydantic import BaseModel, Field
from retrieval import retrieve_top_k


# --- Pydantic models ---

class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(3, ge=1, le=10)


class Chunk(BaseModel):
    chunk_id: int
    text: str
    score: float


class RetrieveResponse(BaseModel):
    retrieved: list[Chunk]


class HealthResponse(BaseModel):
    status: str


# --- App ---

app = FastAPI()


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest) -> RetrieveResponse:
    raw = retrieve_top_k(req.query, req.k)
    return RetrieveResponse(retrieved=[Chunk(**r) for r in raw])


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")