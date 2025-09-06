from proyecto_youtube.db.session import SessionLocal
from proyecto_youtube.db.models import Resultado, Keyword, Canal
from sqlalchemy.orm import joinedload

sess = SessionLocal()

print('Conectando a DB y extrayendo resultados de nicho...')
q = sess.query(Resultado).options(joinedload(Resultado.keyword)).filter(Resultado.canal_id==None).order_by(Resultado.created_at.desc()).limit(20)
rows = q.all()
print(f'Total filas nicho retornadas: {len(rows)}\n')
for r in rows:
    kw = r.keyword.text if r.keyword else 'N/A'
    print(f'id={r.id} | keyword="{kw}" | competencia={r.competencia_tipo} | avg_views={r.recent_avg_views} | created_at={r.created_at}')

sess.close()
