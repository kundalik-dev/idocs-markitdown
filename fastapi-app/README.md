# iDocs — FastAPI

FastAPI backend + static HTML UI for [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```

Open http://localhost:8000.

## API

- `GET /` — web UI (serves `static/index.html`)
- `POST /api/convert` — multipart form field `file`; returns `{ "markdown": "...", "filename": "..." }`

Max upload: 50 MB.

## Project layout

```
app/              FastAPI application (entry: app.main:app)
static/           Static assets for the web UI
requirements.txt  Python dependencies
```
