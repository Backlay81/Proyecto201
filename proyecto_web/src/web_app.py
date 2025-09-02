import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Web Niche Analyzer - Proyecto Web", layout="wide")

st.title("Web Niche Analyzer (Proyecto Web)")
st.markdown("Skeleton de la app Streamlit para análisis web. Ajusta la ruta al script del analizador.")

default_shared = (Path(__file__).resolve().parents[1] / 'utils' / 'niche_analyzer_basic.py')
script_path = st.text_input("Ruta al script del analizador (py)", value=str(default_shared))

# Region/Idioma selector (ES/US)
region_code = st.selectbox("Región", options=['ES', 'US'], index=0)
lang = 'es' if region_code == 'ES' else 'en'

# Optional keywords input (separated by ||)
keywords_input = st.text_input("Keywords (separa con '||', opcional)", value="")

run_button = st.button("Ejecutar análisis web")

if run_button:
    if not os.path.exists(script_path):
        st.error(f"No se encontró el script: {script_path}")
    else:
        # Build command with selected region/lang and optional keywords
        cmd = [sys.executable, script_path, '--region-code', region_code, '--lang', lang]
        if keywords_input.strip():
            cmd += ['--keywords', keywords_input.strip()]

        project_root = str(Path(__file__).resolve().parents[1])
        try:
            res = __import__('subprocess').run(cmd, capture_output=True, text=True, cwd=project_root)
            if res.returncode == 0:
                st.success("Analizador web completado")
                st.code((res.stdout or '')[:1000])
            else:
                st.error("Error ejecutando el analizador web")
                st.code(res.stderr or '(sin stderr)')
        except Exception as e:
            st.error(f"Error: {e}")

st.write("Última verificación: ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
