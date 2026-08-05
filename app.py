import streamlit as st
import pymupdf4llm
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="PDF → Markdown",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Colores principales */
:root {
    --primary: #2563EB;
    --primary-light: #3B82F6;
    --primary-dark: #1D4ED8;
    --accent: #10B981;
    --accent-light: #34D399;
    --danger: #EF4444;
    --bg-dark: #0F172A;
    --bg-card: #1E293B;
    --bg-hover: #334155;
    --text-primary: #F1F5F9;
    --text-secondary: #CBD5E1;
    --text-muted: #94A3B8;
    --border: #1E293B;
}

/* Cabecera principal */
.hero-section {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    padding: 3rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(37, 99, 235, 0.15);
}
.hero-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: white;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.9);
    margin-top: 0.5rem;
}

/* Grid de estadísticas */
.stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
.stat-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}
.stat-card:hover {
    border-color: #2563EB;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.1);
}
.stat-value {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.stat-value.reduction {
    color: #10B981;
}
.stat-value.size {
    color: #3B82F6;
}
.stat-value.tokens {
    color: #F59E0B;
}
.stat-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B;
}

/* Upload area */
.upload-area {
    border: 2px dashed #334155;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    background: rgba(37, 99, 235, 0.02);
}
.upload-area:hover {
    border-color: #2563EB;
    background: rgba(37, 99, 235, 0.05);
}

/* Botón descarga */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.8rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    box-shadow: 0 12px 24px rgba(16, 185, 129, 0.3) !important;
}

/* Success message */
.success-banner {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    padding: 1.2rem;
    border-radius: 10px;
    margin: 1.5rem 0;
    font-weight: 600;
}

/* Historia */
.history-item {
    background: #1E293B;
    border-left: 4px solid #2563EB;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.8rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.history-filename {
    font-weight: 600;
    color: #F1F5F9;
}
.history-stats {
    font-size: 0.85rem;
    color: #94A3B8;
}
.history-reduction {
    font-weight: 700;
    color: #10B981;
}

/* Footer */
.footer {
    font-size: 0.75rem;
    color: #64748B;
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1E293B;
}

/* Expander */
.streamlit-expanderHeader {
    background: #1E293B !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Gestión de historial ───────────────────────────────────────────────────────
HISTORY_FILE = Path(".streamlit_history.json")

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def add_to_history(filename, pdf_kb, md_kb, tokens):
    history = load_history()
    history.insert(0, {
        "filename": filename,
        "pdf_size_kb": round(pdf_kb, 2),
        "md_size_kb": round(md_kb, 2),
        "reduction_percent": round((1 - md_kb / pdf_kb) * 100, 1),
        "tokens_estimated": tokens,
        "timestamp": datetime.now().isoformat()
    })
    save_history(history[:20])  # Guardar últimas 20

# ── Cabecera Hero ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-icon">📄 → 📝</div>
    <h1 class="hero-title">PDF → Markdown</h1>
    <p class="hero-subtitle">
        Convierte documentos PDF a texto limpio. Reduce tokens, mejora análisis con IA.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Layout con columnas ────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Convertir PDF", divider="blue")
    uploaded_file = st.file_uploader(
        "Selecciona un archivo PDF",
        type=["pdf"],
        help="El archivo se procesa localmente, no se almacena."
    )

    if uploaded_file is not None:
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Conversión
        with st.spinner("⚙️ Extrayendo y optimizando..."):
            md_text = pymupdf4llm.to_markdown(tmp_path)

        os.remove(tmp_path)

        # ── Calcular métricas ──────────────────────────────────────────────────
        pdf_kb   = uploaded_file.size / 1024
        md_kb    = len(md_text.encode("utf-8")) / 1024
        reduccion = (1 - md_kb / pdf_kb) * 100
        tokens_est = int(len(md_text) / 4)

        # Guardar en historial
        add_to_history(uploaded_file.name, pdf_kb, md_kb, tokens_est)

        # ── Banner de éxito ────────────────────────────────────────────────────
        st.markdown(
            f'<div class="success-banner">✓ Conversión completada en {pdf_kb:.1f} KB → {md_kb:.1f} KB</div>',
            unsafe_allow_html=True
        )

        # ── Estadísticas ──────────────────────────────────────────────────────
        st.markdown("""
        <div class="stats-container">
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value reduction">−{reduccion:.0f}%</div>
                <div class="stat-label">Reducción</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value size">{md_kb:.1f} KB</div>
                <div class="stat-label">Tamaño final</div>
            </div>
            """, unsafe_allow_html=True)

        with col_c:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value tokens">~{tokens_est:,}</div>
                <div class="stat-label">Tokens est.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Descarga ───────────────────────────────────────────────────────────
        st.download_button(
            label="⬇ Descargar Markdown",
            data=md_text,
            file_name=uploaded_file.name.replace(".pdf", ".md"),
            mime="text/markdown",
        )

        # ── Vista previa ───────────────────────────────────────────────────────
        with st.expander("📖 Ver vista previa"):
            st.text(md_text[:5000])

with col2:
    st.subheader("Historial", divider="blue")
    history = load_history()
    
    if history:
        for item in history[:10]:
            st.markdown(f"""
            <div class="history-item">
                <div>
                    <div class="history-filename">{item['filename'][:20]}...</div>
                    <div class="history-stats">
                        {item['pdf_size_kb']} KB → {item['md_size_kb']} KB
                    </div>
                </div>
                <div class="history-reduction">−{item['reduction_percent']:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sin conversiones aún. Sube un PDF para empezar.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🔒 Sin almacenamiento · Sin cuenta · Conversión local
</div>
""", unsafe_allow_html=True)
