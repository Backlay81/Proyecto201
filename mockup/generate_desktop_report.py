import os
import glob
import shutil
import sys
from datetime import datetime

base = os.path.join(os.path.dirname(__file__), 'out', 'es')
if not os.path.isdir(base):
    print('Base out/es no existe:', base)
    sys.exit(1)

dirs = [d for d in glob.glob(os.path.join(base, '*')) if os.path.isdir(d)]
if not dirs:
    print('No hay subcarpetas en', base)
    sys.exit(1)

latest = max(dirs, key=os.path.getmtime)
csvpath = os.path.join(latest, 'resultados.csv')
if not os.path.exists(csvpath):
    print('No existe', csvpath)
    sys.exit(1)

desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'Script Youtube')
os.makedirs(desktop_dir, exist_ok=True)
shutil.copy2(csvpath, os.path.join(desktop_dir, 'resultados.csv'))

# intentar leer con pandas si está disponible
rows = None
try:
    import pandas as pd
    df = pd.read_csv(csvpath)
except Exception:
    df = None
    import csv
    with open(csvpath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

# construir markdown
md_lines = []
md_lines.append('# Informe YouTube')
md_lines.append('Generado: ' + datetime.now().isoformat())
md_lines.append('')
md_lines.append('## Resumen')
md_lines.append(f'Carpeta origen: {latest}')
if df is not None:
    md_lines.append(f'Registros: {len(df)}')
else:
    md_lines.append(f'Registros: {len(rows)}')
md_lines.append('')
md_lines.append('## Resumen detallado por nicho')

def safe_int(x):
    try:
        return int(float(x))
    except Exception:
        return 0

if df is not None:
    # Coercionar columnas a tipos útiles
    df['avg_views'] = pd.to_numeric(df.get('avg_views', 0), errors='coerce').fillna(0).astype(int)
    df['median_views'] = pd.to_numeric(df.get('median_views', 0), errors='coerce').fillna(0).astype(int)
    df['pct75_views'] = pd.to_numeric(df.get('pct75_views', 0), errors='coerce').fillna(0).astype(int)
    df['max_views'] = pd.to_numeric(df.get('max_views', 0), errors='coerce').fillna(0).astype(int)
    # Score refinado puede venir con distintos nombres
    score_col = 'potencial_total_refinado' if 'potencial_total_refinado' in df.columns else ('score_refinado' if 'score_refinado' in df.columns else None)
    if score_col:
        df[score_col] = pd.to_numeric(df[score_col], errors='coerce').fillna(0)

    # Estadísticas globales
    total = len(df)
    aprobados = len(df[df['decision'] != 'DESCARTADO'])
    descartados = len(df[df['decision'] == 'DESCARTADO'])
    automatizables = len(df[df.get('automatizable') == True]) if 'automatizable' in df.columns else len(df[df.get('automatizable') == 'True']) if 'automatizable' in df.columns else 0
    alta = 0
    if score_col:
        alta = len(df[df[score_col] >= 70])

    md_lines.append(f'- Total nichos: {total}')
    md_lines.append(f'- Nichos aprobados: {aprobados}')
    md_lines.append(f'- Nichos descartados: {descartados}')
    md_lines.append(f'- Automatizables: {automatizables}')
    if score_col:
        md_lines.append(f'- Alta calidad (>{70}): {alta}')
    md_lines.append('')

    # Detalle por nicho (ordenado por score si existe)
    orden = df.sort_values(by=score_col if score_col else 'avg_views', ascending=False)
    for _, r in orden.iterrows():
        md_lines.append(f"### {r.get('keyword','')}")
        md_lines.append(f"- Region: {r.get('region','')}")
        md_lines.append(f"- Decision: {r.get('decision','')}")
        md_lines.append(f"- Motivo / Reason: {r.get('reason','') or r.get('motivo_descarte','')}")
        md_lines.append(f"- Videos analizados: {safe_int(r.get('video_count',0))}")
        md_lines.append(f"- Views promedio: {safe_int(r.get('avg_views',0)):,}")
        md_lines.append(f"- Mediana views: {safe_int(r.get('median_views',0)):,}")
        md_lines.append(f"- Percentil 75 views: {safe_int(r.get('pct75_views',0)):,}")
        md_lines.append(f"- Views máximas: {safe_int(r.get('max_views',0)):,}")
        md_lines.append(f"- Monetización: {r.get('monetizacion','')}")
        md_lines.append(f"- Automatizable: {r.get('automatizable','')} ({r.get('automatizable_count','')}/5)")
        md_lines.append(f"- % videos monetizables: {r.get('porcentaje_monetizables', r.get('analisis_titulos.porcentaje_monetizables',''))}")
        if score_col:
            md_lines.append(f"- Potencial refinado: {r.get(score_col,0)}")
        md_lines.append('')
else:
    # Fallback cuando no hay pandas
    md_lines.append('No se pudo leer con pandas; mostrando primeros registros del CSV')
    for r in (rows or [])[:10]:
        md_lines.append(f"### {r.get('keyword','')}")
        md_lines.append(f"- Region: {r.get('region','')}")
        md_lines.append(f"- Decision: {r.get('decision','')}")
        md_lines.append(f"- Motivo / Reason: {r.get('reason','') or r.get('motivo_descarte','')}")
        md_lines.append(f"- Videos analizados: {r.get('video_count','')}")
        md_lines.append(f"- Views promedio: {r.get('avg_views','')}")
        md_lines.append(f"- Mediana views: {r.get('median_views','')}")
        md_lines.append(f"- Percentil 75 views: {r.get('pct75_views','')}")
        md_lines.append(f"- Views máximas: {r.get('max_views','')}")
        md_lines.append(f"- Monetización: {r.get('monetizacion','')}")
        md_lines.append(f"- Automatizable: {r.get('automatizable','')} ({r.get('automatizable_count','')}/5)")
        md_lines.append(f"- % videos monetizables: {r.get('porcentaje_monetizables','')}")
        md_lines.append(f"- Potencial refinado: {r.get('potencial_total_refinado', r.get('score_refinado',''))}")
        md_lines.append('')

md_path = os.path.join(desktop_dir, 'resultados.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print('OK', desktop_dir, os.path.join(desktop_dir, 'resultados.csv'), md_path)
