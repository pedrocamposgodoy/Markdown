import streamlit as st
import pymupdf4llm
import tempfile
import os

st.set_page_config(
    page_title="PDF → Markdown",
    page_icon="📄",
    layout="centered",
)

# ── CSS personalizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Cabecera */
.header-block {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid #1E293B;
    margin-bottom: 2rem;
}
.header-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3B82F6;
    margin-bottom: 0.4rem;
}
.header-title {
    font-size: 2rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 0;
    line-height: 1.2;
}
.header-sub {
    font-size: 0.95rem;
    color: #94A3B8;
    margin-top: 0.5rem;
}

/* Tarjeta de stats */
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
    margin: 1.5rem 0;
}
.stat-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #3B82F6;
    line-height: 1;
}
.stat-value.highlight {
    color: #22D3EE;
}
.stat-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748B;
    margin-top: 0.4rem;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #1E293B;
    margin: 1.5rem 0;
}

/* Botón de descarga de Streamlit - override */
div[data-testid="stDownloadButton"] > button {
    background: #3B82F6 !important;
    color: white !important;
    border: none !important;
    padding: 0.6rem 1.5rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: #2563EB !important;
}

/* Footer */
.footer {
    font-size: 0.72rem;
    color: #334155;
    text-align: center;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #1E293B;
}
</style>
""", unsafe_allow_html=True)

# ── Cabecera ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-block">
    <div class="header-label">Herramienta de optimización</div>
    <div class="header-title">PDF → Markdown</div>
    <div class="header-sub">
        Convierte documentos PDF a texto limpio para reducir el gasto de tokens en IA.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Subida de archivo ──────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Selecciona un archivo PDF",
    type=["pdf"],
    help="El archivo se procesa localmente, no se almacena en ningún servidor."
)

if uploaded_file is not None:

    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Conversión
    with st.spinner("Extrayendo texto..."):
        md_text = pymupdf4llm.to_markdown(tmp_path)

    os.remove(tmp_path)

    # ── Calcular métricas ──────────────────────────────────────────────────────
    pdf_kb   = uploaded_file.size / 1024
    md_kb    = len(md_text.encode("utf-8")) / 1024
    reduccion = (1 - md_kb / pdf_kb) * 100
    tokens_est = int(len(md_text) / 4)

    # ── Stats ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value highlight">−{reduccion:.0f}%</div>
            <div class="stat-label">Reducción de peso</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{md_kb:.0f} KB</div>
            <div class="stat-label">Tamaño resultante</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">~{tokens_est:,}</div>
            <div class="stat-label">Tokens estimados</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Descarga ───────────────────────────────────────────────────────────────
    st.download_button(
        label="⬇  Descargar Markdown",
        data=md_text,
        file_name=uploaded_file.name.replace(".pdf", ".md"),
        mime="text/markdown",
    )

    # ── Vista previa ───────────────────────────────────────────────────────────
    with st.expander("Vista previa del contenido"):
        st.text(md_text[:4000])

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Sin almacenamiento · Sin cuenta · Conversión local
</div>
""", unsafe_allow_html=True)
