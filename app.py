import streamlit as st
import pymupdf4llm
import tempfile
import os

st.set_page_config(page_title="PDF a Markdown", layout="centered")
st.title("Conversor de PDF a Markdown")
st.write(
    "Sube un PDF y descarga su contenido en formato Markdown: "
    "más ligero y más fácil de analizar con IA que el PDF original."
)

uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("Convirtiendo..."):
        md_text = pymupdf4llm.to_markdown(tmp_path)

    os.remove(tmp_path)

    st.success("Conversión completada")

    st.download_button(
        label="Descargar Markdown",
        data=md_text,
        file_name=uploaded_file.name.replace(".pdf", ".md"),
        mime="text/markdown",
    )

    with st.expander("Ver vista previa (primeros 3000 caracteres)"):
        st.text(md_text[:3000])

    st.caption(f"Tamaño original PDF: {uploaded_file.size / 1024:.1f} KB · "
               f"Tamaño Markdown: {len(md_text.encode('utf-8')) / 1024:.1f} KB")
