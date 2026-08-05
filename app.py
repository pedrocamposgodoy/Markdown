import streamlit as st
import fitz  # pymupdf
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="PDF → Markdown",
    page_icon="📄",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero-section {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(37, 99, 235, 0.15);
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: white;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.9);
    margin-top: 0.5rem;
}
.stat-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.5rem;
}
.stat-value { font-size: 2.2rem; font-weight: 800; line-height: 1; margin-bottom: 0.4rem; }
.stat-value.reduction { color: #10B981; }
.stat-value.size      { color: #3B82F6; }
.stat-value.tokens    { color: #F59E0B; }
.stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B;
}
.success-banner {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    padding: 1.2rem;
    border-radius: 10px;
    margin: 1.5rem 0;
    font-weight: 600;
}
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.8rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
}
.history-item {
    background: #1E293B;
    border-left: 4px solid #2563EB;
    padding: 0.9rem 1rem;
    border-radius: 8px;
    margin: 0.6rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.history-filename { font-weight: 600; color: #F1F5F9; font-size: 0.85rem; }
.history-stats    { font-size: 0.78rem; color: #94A3B8; }
.history-reduction { font-weight: 700; color: #10B981; }
.footer {
    font-size: 0.75rem;
    color: #64748B;
    text-align: center;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #1E293B;
}
</style>
""", unsafe_allow_html=True)

# ── Historial ──────────────────────────────────────────────────────────────────
HISTORY_FILE = Path(".pdf_history.json")

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_history(filename, pdf_kb, md_kb, tokens):
    history = load_history()
    history.insert(0, {
        "filename": filename,
        "pdf_kb": round(pdf_kb, 1),
        "md_kb": round(md_kb, 1),
        "reduction": round((1 - md_kb / pdf_kb) * 100, 1),
        "tokens": tokens,
        "date": datetime.now().strftime("%d/%m %H:%M"),
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[:20], f)

# ── Conversión con pymupdf (fitz) ──────────────────────────────────────────────
def pdf_to_markdown(pdf_path):
    doc = fitz.open(pdf_path)
    parts = []
    for i, page in enumerate(doc, 1):
        text = page.get_text("text").strip()
        if text:
            parts.append(f"## Página {i}\n\n{text}")
    doc.close()
    return "\n\n---\n\n".join(parts)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📄 → 📝 PDF a Markdown</div>
    <div class="hero-subtitle">
        Convierte documentos PDF a texto limpio · Reduce tokens · Mejora el análisis con IA
    </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────────
col_main, col_hist = st.columns([2, 1])

with col_main:
    st.subheader("Convertir PDF", divider="blue")
    uploaded_file = st.file_uploader("Selecciona un PDF", type=["pdf"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner("⚙️ Convirtiendo..."):
            md_text = pdf_to_markdown(tmp_path)

        os.remove(tmp_path)

        pdf_kb    = uploaded_file.size / 1024
        md_kb     = len(md_text.encode("utf-8")) / 1024
        reduccion = (1 - md_kb / pdf_kb) * 100
        tokens    = int(len(md_text) / 4)

        save_to_history(uploaded_file.name, pdf_kb, md_kb, tokens)

        st.markdown(
            f'<div class="success-banner">✓ {uploaded_file.name} · '
            f'{pdf_kb:.0f} KB → {md_kb:.0f} KB</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-value reduction">−{reduccion:.0f}%</div><div class="stat-label">Reducción</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-value size">{md_kb:.1f} KB</div><div class="stat-label">Tamaño final</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-value tokens">~{tokens:,}</div><div class="stat-label">Tokens est.</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.download_button(
            label="⬇ Descargar Markdown",
            data=md_text,
            file_name=uploaded_file.name.replace(".pdf", ".md"),
            mime="text/markdown",
        )

        with st.expander("📖 Vista previa"):
            st.text(md_text[:5000])

with col_hist:
    st.subheader("Historial", divider="blue")
    history = load_history()
    if history:
        for item in history[:10]:
            name = item['filename']
            name_short = name[:18] + "…" if len(name) > 18 else name
            st.markdown(f"""
            <div class="history-item">
                <div>
                    <div class="history-filename">{name_short}</div>
                    <div class="history-stats">{item['pdf_kb']} KB → {item['md_kb']} KB · {item['date']}</div>
                </div>
                <div class="history-reduction">−{item['reduction']:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sin conversiones aún.")

st.markdown('<div class="footer">🔒 Sin almacenamiento · Sin cuenta · Conversión local</div>', unsafe_allow_html=True)
