# iDocs — Streamlit

Streamlit UI for [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

Opens at http://localhost:8501.

## Deploy (free)

Streamlit Community Cloud — https://share.streamlit.io
- Point it at this repo, set the app path to `streamlit-app/streamlit_app.py`.
- Max upload is enforced in-app at 50 MB.
