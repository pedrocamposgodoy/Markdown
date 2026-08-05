# PDF a Markdown

App sencilla en Streamlit que convierte un PDF en Markdown, para reducir peso
y facilitar su análisis con modelos de IA (menos tokens, contenido más limpio).

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abrirá en el navegador en `http://localhost:8501`.

## Desplegar en Streamlit Cloud (gratis)

1. Sube esta carpeta a un repositorio de GitHub (puede ser público o privado).
2. Entra en https://share.streamlit.io con tu cuenta de GitHub.
3. Pulsa "New app", selecciona el repo y el archivo `app.py`.
4. Despliega. Te dará una URL pública tipo `tuapp.streamlit.app` que puedes
   compartir directamente, sin que la otra persona instale nada.

## Archivos

- `app.py` — la aplicación
- `requirements.txt` — dependencias (streamlit, pymupdf4llm)
- `README.md` — este archivo
