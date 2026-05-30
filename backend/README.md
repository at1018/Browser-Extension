# AI Visual Copilot Backend

This backend folder contains a minimal FastAPI scaffold to support the extension integration.

## Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /health`
- `POST /api/screenshots/analyze`

The analyze endpoint currently returns a placeholder response for Phase 2.
