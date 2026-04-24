# iDocs

Convert PDFs, Office files, images, HTML, and more into Markdown using [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

This repo contains two independent apps:

- **[`streamlit-app/`](./streamlit-app)** — Streamlit UI. Easiest free deploy via Streamlit Community Cloud.
- **[`fastapi-app/`](./fastapi-app)** — FastAPI backend + static HTML UI. Deployable to Hugging Face Spaces (Docker), Render, Fly.io, etc.

Each folder has its own `requirements.txt` and `README.md`. Pick whichever fits your use case and follow its README.

## Requirements

Python 3.10–3.12 recommended — MarkItDown's native deps (`onnxruntime`, `magika`) may fail to build on newer Python versions on Windows.
