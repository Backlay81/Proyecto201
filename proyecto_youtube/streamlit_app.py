"""
Streamlit UI para probar el analizador unificado de nichos YouTube.
Coloca este archivo en `proyecto_youtube/` y ejecútalo con:

  python -m streamlit run streamlit_app.py

La app permite introducir keywords (separadas por coma), región e idioma,
lanza el análisis y muestra resultados. También permite descargar el CSV.
"""
import sys
import os
import subprocess
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="YouTube Niche Analyzer", layout="wide")

st.title("YouTube Niche Analyzer — Streamlit")
st.markdown("Interfaz similar a la app web: selecciona región, keywords (separadas por '||') y ejecuta el analizador CLI para obtener CSV y MD idénticos a la salida de terminal.")

# Selector de script (por si quieres usar otra ruta)
# Por organización, el analizador unificado está en `analyzers/` y las herramientas en `tools/`.
default_script = ROOT / 'nichos_youtube.py'
script_path = st.text_input("Ruta al script del analizador (py)", value=str(default_script))

# Región / idioma
region = st.selectbox("Región", options=['ES', 'US'], index=0)
lang = 'es' if region == 'ES' else 'en'

# Keywords input (separador '||' para múltiples)
keywords_input = st.text_input("Keywords (separa con '||')", value="mejores aspiradoras 2025")

output_prefix = st.text_input("Prefijo de salida (archivo)", value="streamlit_run")

# Selector para numero maximo de videos a analizar
max_results = st.number_input("Max results (nº de vídeos a analizar)", min_value=1, max_value=200, value=50, step=1)

run_button = st.button("Ejecutar análisis")

if run_button:
    # Validaciones básicas
    if not os.path.exists(script_path):
        st.error(f"No se encontró el script: {script_path}")
    else:
        kws = [k.strip() for k in keywords_input.split('||') if k.strip()]
        if not kws:
            st.warning("Introduce al menos una keyword")
        else:
            cmd = [sys.executable, script_path] + kws + ['--region', region, '--language', lang, '--output', output_prefix, '--max-results', str(int(max_results))]
            project_root = str(ROOT)

            try:
                with st.spinner("Ejecutando analizador (esto puede tardar un poco)..."):
                    res = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)

                if res.returncode == 0:
                    st.success("Analizador completado correctamente")
                    # Mostrar stdout parcialmente
                    st.code((res.stdout or '')[:3000])

                    # Buscar archivos generados en out/
                    out_dir = ROOT / 'out'
                    files = sorted(out_dir.glob(f"{output_prefix}_*.csv"))
                    md_files = sorted(out_dir.glob(f"{output_prefix}_*.md"))

                    if files:
                        latest_csv = files[-1]
                        st.markdown(f"**CSV generado:** {latest_csv}")
                        st.download_button("Descargar CSV", data=latest_csv.read_bytes(), file_name=latest_csv.name, mime='text/csv')
                    else:
                        st.warning("No se encontró CSV generado en 'out/'")

                    if md_files:
                        latest_md = md_files[-1]
                        st.markdown(f"**MD generado:** {latest_md}")
                        st.download_button("Descargar MD", data=latest_md.read_bytes(), file_name=latest_md.name, mime='text/markdown')
                    else:
                        st.warning("No se encontró MD generado en 'out/'")

                else:
                    st.error("El analizador falló al ejecutarse")
                    st.code(res.stderr or '(sin stderr)')

            except Exception as e:
                st.error(f"Error lanzando el analizador: {e}")

st.write("\n---\nStreamlit app creada en `proyecto_youtube/streamlit_app.py`\nOrganización sugerida:\n- Analizador unificado: `proyecto_youtube/nichos_youtube.py`\n- Buscador de canales: `proyecto_youtube/canales_youtube/buscar_canales_youtube.py`\nAmbos scripts escriben outputs en `proyecto_youtube/out/`.")
