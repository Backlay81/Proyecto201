import os
import glob
import sys
import shutil
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

# output html path on desktop
desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'Script Youtube')
os.makedirs(desktop_dir, exist_ok=True)
html_path = os.path.join(desktop_dir, 'resultados.html')

# read CSV
try:
    import pandas as pd
    df = pd.read_csv(csvpath)
except Exception:
    # fallback simple CSV parse
    import csv
    with open(csvpath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    df = None

# helpers for rendering
def emoji_for_decision(dec):
    if dec == 'RECOMENDADO':
        return '🚀', '#1e7e34'
    if dec == 'EVALUAR':
        return '⭐', '#ffc107'
    return '❌', '#dc3545'

def color_for_saturation(s):
    try:
        s_str = str(s or '')
    except Exception:
        s_str = ''
    if 'Bajo' in s_str:
        return 'green'
    if 'Medio' in s_str:
        return 'orange'
    return 'red'

# build HTML
html = []
html.append('<!doctype html>')
html.append('<html><head><meta charset="utf-8"><title>Resultados YouTube</title>')
html.append('<style>body{font-family:Segoe UI,Roboto,Arial,sans-serif;background:#f7f7f9;color:#222;padding:20px}h1{margin-top:0}table{border-collapse:collapse;width:100%;background:#fff}th,td{padding:8px;border:1px solid #e1e1e8;text-align:left}th{background:#f0f0f3} .badge{display:inline-block;padding:4px 8px;border-radius:12px;color:#fff;font-weight:600} .muted{color:#666} .small{font-size:0.9em} .card{background:#fff;padding:12px;border-radius:8px;box-shadow:0 1px 2px rgba(0,0,0,0.04);margin-bottom:12px}</style>')
html.append('</head><body>')
html.append('<h1>Informe YouTube</h1>')
html.append(f'<p class="muted">Generado: {datetime.now().isoformat()}</p>')
html.append(f'<p class="small">Fuente: {latest} — CSV: resultados.csv</p>')

# summary and table
if df is not None:
    df['avg_views'] = pd.to_numeric(df.get('avg_views', 0), errors='coerce').fillna(0).astype(int)
    df['median_views'] = pd.to_numeric(df.get('median_views', 0), errors='coerce').fillna(0).astype(int)
    df['pct75_views'] = pd.to_numeric(df.get('pct75_views', 0), errors='coerce').fillna(0).astype(int)
    score_col = 'potencial_total_refinado' if 'potencial_total_refinado' in df.columns else ('score_refinado' if 'score_refinado' in df.columns else None)
    if score_col:
        df[score_col] = pd.to_numeric(df[score_col], errors='coerce').fillna(0)

    total = len(df)
    descartados = len(df[df['decision'] == 'DESCARTADO']) if 'decision' in df.columns else 0
    aprobados = total - descartados
    html.append(f'<div class="card"><strong>Total nichos:</strong> {total} &nbsp;&nbsp; <strong>Aprobados:</strong> {aprobados} &nbsp;&nbsp; <strong>Descartados:</strong> {descartados}</div>')

    # detail cards
    for _, r in df.iterrows():
        emoji, color = emoji_for_decision(r.get('decision',''))
        saturation = r.get('riesgo_saturacion','')
        sat_color = color_for_saturation(saturation)
        html.append('<div class="card">')
        html.append(f'<h2>{emoji} {r.get("keyword","")}</h2>')
        html.append(f'<p class="muted small">Region: {r.get("region","-")}</p>')
        html.append('<table>')
        html.append('<tr><th>Decision</th><td><span class="badge" style="background:%s">%s</span> %s</td></tr>' % (color, r.get('decision',''), r.get('reason','')))
        html.append('<tr><th>Videos</th><td>%s</td></tr>' % (r.get('video_count','')))
        html.append('<tr><th>Avg views</th><td>%s</td></tr>' % (f"{int(r.get('avg_views',0)):,}"))
        html.append('<tr><th>Median views</th><td>%s</td></tr>' % (f"{int(r.get('median_views',0)):,}"))
        html.append('<tr><th>Pct75 views</th><td>%s</td></tr>' % (f"{int(r.get('pct75_views',0)):,}"))
        html.append('<tr><th>Max views</th><td>%s</td></tr>' % (f"{int(r.get('max_views',0)):,}" if r.get('max_views') else '-'))
        html.append('<tr><th>Monetización</th><td>%s</td></tr>' % (r.get('monetizacion','')))
        html.append('<tr><th>Automatizable</th><td>%s (%s/5)</td></tr>' % (str(r.get('automatizable','')), r.get('automatizable_count','')))
        html.append('<tr><th>% videos monetizables</th><td>{}</td></tr>'.format(r.get('analisis_titulos.porcentaje_monetizables', r.get('porcentaje_monetizables', ''))))
        if score_col:
            html.append('<tr><th>Potencial refinado</th><td>%s</td></tr>' % (r.get(score_col,0)))
        html.append('</table>')
        html.append('</div>')
else:
    # fallback: simple table from rows
    html.append('<div class="card"><em>No se pudo leer CSV con pandas; mostrando tabla básica</em></div>')
    html.append('<table>')
    if rows:
        headers = rows[0].keys()
        html.append('<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>')
        for r in rows:
            html.append('<tr>' + ''.join(f'<td>{r.get(h,"")}</td>' for h in headers) + '</tr>')
    html.append('</table>')

html.append('</body></html>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html))

print('HTML generado en', html_path)
