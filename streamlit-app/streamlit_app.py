"""iDocs (Streamlit): convert uploads to Markdown via Microsoft MarkItDown."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException

MAX_UPLOAD_MB = 50

st.set_page_config(page_title="iDocs — MarkItDown", page_icon="📝", layout="wide")

st.markdown(
    """
    <style>
    /* Page */
    .block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1440px; }

    /* Header */
    h1.idocs-title { font-size: 1.4rem; font-weight: 700; margin: 0 0 .3rem; letter-spacing: -0.02em; }
    .idocs-sub { color: #64748b; font-size: .9rem; margin: 0 0 1rem; line-height: 1.5; }
    .idocs-sub a { color: #2563eb; }

    /* Pane headers */
    .pane-header {
      font-size: .7rem; font-weight: 600; text-transform: uppercase; letter-spacing: .08em;
      color: #64748b; padding: .55rem 1rem; background: #f8fafc;
      border: 1px solid rgba(15,23,42,.08); border-bottom: none;
      border-radius: 8px 8px 0 0;
    }
    .pane-body {
      border: 1px solid rgba(15,23,42,.08); border-radius: 0 0 8px 8px; background: #fff;
      min-height: 540px; padding: 1rem 1.15rem; overflow: auto; max-height: 640px;
    }

    /* Monospace textarea */
    textarea {
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace !important;
      font-size: 13px !important; line-height: 1.6 !important;
      background: #fff !important;
    }

    /* Hide file uploader dropzone completely — show ONLY the Browse button */
    [data-testid="stFileUploaderDropzone"] {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        min-height: 0 !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
    [data-testid="stFileUploaderDropzone"] button {
        margin: 0 !important;
        background: #2563eb !important;
        color: #fff !important;
        border: none !important;
        padding: 0 1rem !important;
        height: 38px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: .8125rem !important;
        width: auto !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        background: #1d4ed8 !important;
    }
    /* Hide only the top widget label, not inner labels (browse button may BE a label) */
    [data-testid="stFileUploader"] > label { display: none !important; }
    [data-testid="stFileUploader"] { padding: 0 !important; }
    /* Style the browse button/label inside dropzone */
    [data-testid="stFileUploaderDropzone"] > label,
    [data-testid="stFileUploaderDropzone"] > button,
    [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {
        background: #2563eb !important;
        color: #fff !important;
        border: none !important;
        height: 38px !important;
        padding: 0 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: .8125rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }
    [data-testid="stFileUploaderDropzone"] > label:hover,
    [data-testid="stFileUploaderDropzone"] > button:hover {
        background: #1d4ed8 !important;
    }

    /* Unify all toolbar button heights */
    .stButton > button,
    .stDownloadButton > button {
        height: 38px !important;
        padding: 0 .95rem !important;
        font-size: .8125rem !important;
        border-radius: 8px !important;
    }

    /* Uploaded file chip — compact, horizontal, no extra "+" button */
    [data-testid="stFileUploaderFile"] {
        padding: .2rem .4rem !important;
        font-size: .72rem !important;
        margin: 0 !important;
        background: transparent !important;
    }
    [data-testid="stFileUploaderFile"] small { font-size: .65rem !important; }
    [data-testid="stFileUploaderFileData"] { gap: .35rem !important; }
    [data-testid="stFileUploaderFileData"] div:first-child { display: none !important; }
    /* Hide the "+" add-more-files button that appears after upload
       (but NOT the Browse button inside the dropzone — it's also kind=secondary) */
    [data-testid="stFileUploaderAddFile"],
    [data-testid="stFileUploaderDeleteBtn"] + button {
        display: none !important;
    }
    /* Hide file uploader section list extras */
    [data-testid="stFileUploader"] > section > div > div:nth-child(n+3) {
        display: none !important;
    }
    /* Compact the whole uploader after file is chosen */
    [data-testid="stFileUploader"] > section {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: .5rem !important;
        flex-wrap: nowrap !important;
    }
    /* Show the Browse button inside the dropzone */
    [data-testid="stFileUploaderDropzone"] button {
        display: inline-flex !important;
        align-items: center;
    }
    /* Hide delete button's default styling but keep it clickable */
    [data-testid="stFileUploaderDeleteBtn"] { display: inline-flex !important; }
    /* After a file is chosen, hide the whole dropzone entirely */
    [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzone"] {
        display: none !important;
    }
    /* Style the delete (X) btn as a small neutral circle */
    [data-testid="stFileUploaderDeleteBtn"] {
        background: transparent !important;
        color: #64748b !important;
        border: none !important;
        padding: 2px !important;
        height: 22px !important;
        width: 22px !important;
        min-height: 0 !important;
    }
    [data-testid="stFileUploaderDeleteBtn"]:hover { color: #ef4444 !important; }

    /* Segmented radio for view tabs */
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        gap: .25rem;
        background: #f1f5f9;
        padding: 3px;
        border-radius: 8px;
        width: fit-content;
        border: 1px solid rgba(15,23,42,.08);
    }
    div[data-testid="stRadio"] label {
        margin: 0 !important;
        padding: .35rem .85rem !important;
        border-radius: 6px;
        cursor: pointer;
        font-size: .8125rem !important;
        font-weight: 500;
        color: #64748b !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #fff;
        color: #0f172a !important;
        box-shadow: 0 1px 3px rgba(15,23,42,.08);
    }
    div[data-testid="stRadio"] label > div:first-child { display: none !important; }

    /* Primary button (Convert) */
    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: #fff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover:not(:disabled) {
        background: #1d4ed8 !important;
    }
    .stButton > button[kind="primary"]:disabled {
        background: #e2e8f0 !important;
        color: #94a3b8 !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }
    /* Secondary / download buttons */
    .stButton > button[kind="secondary"],
    .stDownloadButton > button {
        background: #fff !important;
        color: #0f172a !important;
        border: 1px solid rgba(15,23,42,.12) !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover:not(:disabled),
    .stDownloadButton > button:hover:not(:disabled) {
        border-color: #2563eb !important;
        background: rgba(37,99,235,.06) !important;
    }
    .stDownloadButton > button:disabled {
        background: #f8fafc !important;
        color: #94a3b8 !important;
        border-color: rgba(15,23,42,.08) !important;
        opacity: 1 !important;
    }

    /* Force every toolbar column onto same baseline */
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] > [data-testid="stVerticalBlock"] {
        width: 100%;
    }

    /* Tighten vertical spacing inside card */
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] { gap: .5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_converter() -> MarkItDown:
    return MarkItDown(enable_plugins=False)


def convert(file_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower() or ".bin"
    result = get_converter().convert_stream(BytesIO(file_bytes), file_extension=suffix)
    return result.text_content


def copy_button(text: str, key: str = "copy") -> None:
    payload = json.dumps(text)
    components.html(
        f"""
        <div style="display:flex;align-items:center;gap:8px;font-family:'Inter',system-ui,sans-serif">
          <button id="cp-{key}" style="
            cursor:pointer;height:38px;padding:0 .95rem;border-radius:8px;
            background:#fff;color:#0f172a;border:1px solid rgba(15,23,42,.12);
            font-weight:500;font-size:13px;transition:all .15s;display:inline-flex;align-items:center;gap:4px">
            📋 Copy Markdown
          </button>
          <span id="st-{key}" style="font-size:12px;color:#22c55e"></span>
        </div>
        <script>
          const btn = document.getElementById("cp-{key}");
          const status = document.getElementById("st-{key}");
          btn.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText({payload});
              status.textContent = "✓ Copied";
              setTimeout(() => status.textContent = "", 1800);
            }} catch (e) {{
              status.textContent = "Copy failed";
            }}
          }});
          btn.addEventListener("mouseenter", () => {{
            btn.style.borderColor = "#2563eb";
            btn.style.background = "rgba(37,99,235,.06)";
          }});
          btn.addEventListener("mouseleave", () => {{
            btn.style.borderColor = "rgba(15,23,42,.12)";
            btn.style.background = "#fff";
          }});
        </script>
        """,
        height=42,
    )


# ---------- state ----------
if "markdown" not in st.session_state:
    st.session_state.markdown = ""
    st.session_state.basename = "document"
if "editor_nonce" not in st.session_state:
    st.session_state.editor_nonce = 0

# ---------- header ----------
st.markdown('<h1 class="idocs-title">iDocs</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="idocs-sub">Turn PDFs, Office files, images, HTML, and more into Markdown with '
    '<a href="https://github.com/microsoft/markitdown" target="_blank">Microsoft MarkItDown</a>.'
    '<br/>Switch views below to edit source, preview, or see both.</p>',
    unsafe_allow_html=True,
)

# ---------- toolbar (one card) ----------
with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns([1.6, 0.9, 1.3, 1.3, 2.9], vertical_alignment="center")
    with c1:
        uploaded = st.file_uploader(
            "file", type=None, label_visibility="collapsed", key="uploader"
        )
    with c2:
        do_convert = st.button(
            "Convert", type="primary", disabled=uploaded is None, use_container_width=True
        )
    with c3:
        _live_key = f"editor_text_{st.session_state.editor_nonce}"
        copy_source = st.session_state.get(_live_key) or st.session_state.markdown or ""
        copy_button(copy_source, key=f"top_{st.session_state.editor_nonce}")
    with c4:
        _live_key = f"editor_text_{st.session_state.editor_nonce}"
        st.download_button(
            "⬇ Download .md",
            data=(st.session_state.get(_live_key) or st.session_state.markdown or "").encode("utf-8"),
            file_name=f"{st.session_state.basename}.md",
            mime="text/markdown",
            disabled=not st.session_state.markdown,
            use_container_width=True,
        )
    with c5:
        fname = uploaded.name if uploaded else "No file selected"
        st.markdown(
            f'<div style="color:#64748b;font-size:.85rem;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis">{fname}</div>',
            unsafe_allow_html=True,
        )

    # separator + view tabs
    st.markdown(
        '<hr style="margin:.5rem 0 .75rem;border:none;border-top:1px solid rgba(15,23,42,.08)"/>',
        unsafe_allow_html=True,
    )

    vcols = st.columns([3, 2])
    with vcols[0]:
        view = st.radio(
            "view",
            ["Split", "Markdown", "Preview"],
            horizontal=True,
            label_visibility="collapsed",
            key="view",
        )
    with vcols[1]:
        hints = {
            "Split": "Source and preview side by side",
            "Markdown": "Markdown source only — edit and copy",
            "Preview": "Rendered preview only",
        }
        st.markdown(
            f'<div style="text-align:right;color:#64748b;font-size:.8rem;padding-top:.55rem">{hints[view]}</div>',
            unsafe_allow_html=True,
        )

# ---------- convert ----------
if do_convert and uploaded is not None:
    raw = uploaded.getvalue()
    if len(raw) > MAX_UPLOAD_MB * 1024 * 1024:
        st.error(f"File too large (max {MAX_UPLOAD_MB} MB).")
    else:
        with st.spinner("Converting…"):
            try:
                st.session_state.markdown = convert(raw, uploaded.name)
                st.session_state.basename = Path(uploaded.name).stem or "document"
                st.session_state.editor_nonce += 1
                st.rerun()
            except UnsupportedFormatException as e:
                st.error(f"Unsupported format: {e}")
            except FileConversionException as e:
                st.error(f"Could not convert file: {e}")
            except Exception as e:
                st.error(f"Conversion failed: {e}")

# ---------- content panes ----------
editor_key = f"editor_text_{st.session_state.editor_nonce}"
md_value = st.session_state.get(editor_key, st.session_state.markdown)
placeholder = "Choose a file and click Convert, or paste Markdown here…"

st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

if view == "Split":
    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown('<div class="pane-header">Markdown source</div>', unsafe_allow_html=True)
        md_value = st.text_area(
            "editor",
            value=md_value,
            height=560,
            label_visibility="collapsed",
            key=editor_key,
            placeholder=placeholder,
        )
    with right:
        st.markdown('<div class="pane-header">Rendered preview</div>', unsafe_allow_html=True)
        with st.container(height=560, border=True):
            if md_value.strip():
                st.markdown(md_value, unsafe_allow_html=False)
            else:
                st.markdown(f'<span style="color:#94a3b8">{placeholder}</span>', unsafe_allow_html=True)

elif view == "Markdown":
    st.markdown('<div class="pane-header">Markdown source</div>', unsafe_allow_html=True)
    md_value = st.text_area(
        "editor",
        value=md_value,
        height=640,
        label_visibility="collapsed",
        key=editor_key,
        placeholder=placeholder,
    )

elif view == "Preview":
    st.markdown('<div class="pane-header">Rendered preview</div>', unsafe_allow_html=True)
    with st.container(height=640, border=True):
        if md_value.strip():
            st.markdown(md_value, unsafe_allow_html=False)
        else:
            st.markdown(f'<span style="color:#94a3b8">{placeholder}</span>', unsafe_allow_html=True)
