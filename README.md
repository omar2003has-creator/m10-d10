# Drill 10 — Typed Retrieval Endpoint

Build a single-endpoint FastAPI service with Pydantic-validated request
and response shapes plus a `/healthz` liveness probe.

> Read the full Drill page on the cohort site:
> <https://LevelUp-Applied-AI.github.io/aispire-14005-pages/modules/module-10/1d100b5a>

## Setup

The Module 10 package install lives in the Reading. If you have not
already installed the M10 packages, complete that install first.

Install dependencies (cached from the Reading install — should be fast):

```bash
pip install -r requirements.txt
```

Run the service locally:

```bash
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the OpenAPI surface.

## Verify

```bash
pytest tests/ -v
```

`pytest` against the unmodified starter must fail — that's the gate.

## Submission

Fork-and-submit per the M8+ pattern. See `FORK-SUBMIT.md`.

---

## License

This repository is provided for educational use only. See
[LICENSE](LICENSE) for terms. You may clone and modify this repository
for personal learning and practice, and reference code you wrote here
in your professional portfolio. Redistribution outside this course is
not permitted.
