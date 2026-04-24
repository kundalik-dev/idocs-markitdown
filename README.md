# iDocs

Convert PDFs, Office files, images, HTML, and more into Markdown using [Microsoft MarkItDown](https://github.com/microsoft/markitdown), served through a small FastAPI web UI.

## Requirements

- Python 3.10–3.12 recommended (MarkItDown's native deps — `onnxruntime`, `magika` — may fail to build on newer versions on Windows).
- The existing `.venv` in this repo was built with Python 3.14 and works, but stick to 3.10–3.12 if you recreate it.

## Quick start (returning to this project)

If `.venv` already exists in the repo root, just activate it and run the server:

```bash
# Windows (cmd)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

python -m uvicorn app.main:app --port 8000 --reload
```

Then open http://localhost:8000.

## First-time setup

1. Create the virtual environment (the repo uses `.venv`, not `venv`):

   ```bash
   python -m venv .venv
   ```

2. Activate it (see commands above).

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Verify the venv is the one being used — this is the #1 source of "module not found" errors:

   ```bash
   # Windows
   where python
   python -m uvicorn --version

   # macOS / Linux
   which python
   python -m uvicorn --version
   ```

   The `python` path must point inside `.venv`. If it points to `C:\Program Files\Python3xx\python.exe` (or `/usr/bin/python`), the venv isn't active.

## Run

```bash
python -m uvicorn app.main:app --port 8000
```

Use `--reload` during development to auto-restart on code changes:

```bash
python -m uvicorn app.main:app --port 8000 --reload
```

Stop the server with `Ctrl+C`.

## Open in browser

Open **http://localhost:8000** — **not** `http://localhost:3000`.

> The FastAPI server listens on port **8000**. Hitting port 3000 (or any other port) will fail, and `POST`-ing directly to `/api/convert` via the address bar returns **405 Method Not Allowed** because browsers issue `GET` there. Always upload via the UI on port 8000.

## API

- `GET /` — web UI
- `POST /api/convert` — multipart form field `file`; returns `{ "markdown": "...", "filename": "..." }`

Max upload size: 50 MB.

## Troubleshooting

- **`No module named uvicorn`** — your shell is using the system Python. Activate `.venv` (see above) and confirm with `where python` / `which python`.
- **PowerShell blocks `Activate.ps1`** — run once per user:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```
- **`pip install` fails on `onnxruntime` or `magika`** — use Python 3.10–3.12. Newer versions don't always have prebuilt wheels on Windows.
- **Port 8000 already in use** — run on a different port: `python -m uvicorn app.main:app --port 8001`.

## Project layout

```
app/              FastAPI application (entry: app.main:app)
static/           Static assets for the web UI
requirements.txt  Python dependencies
.venv/            Local virtual environment (not committed)
```
