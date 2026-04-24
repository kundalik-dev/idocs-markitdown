"""iDocs: convert uploads to Markdown via Microsoft MarkItDown, with a small web UI."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

app = FastAPI(title="iDocs", description="Convert files to Markdown with MarkItDown")

_md: MarkItDown | None = None


def get_converter() -> MarkItDown:
    global _md
    if _md is None:
        _md = MarkItDown(enable_plugins=False)
    return _md


@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Upload must include a filename (for format detection).")
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB).",
        )

    suffix = Path(file.filename).suffix
    if not suffix:
        suffix = ".bin"

    converter = get_converter()
    try:
        result = converter.convert_stream(BytesIO(raw), file_extension=suffix.lower())
    except UnsupportedFormatException as e:
        raise HTTPException(status_code=415, detail=str(e)) from e
    except FileConversionException as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e!s}") from e

    return JSONResponse(
        {
            "markdown": result.text_content,
            "filename": file.filename,
        }
    )


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")
