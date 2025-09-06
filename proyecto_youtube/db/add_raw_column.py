import sqlite3
p = 'proyecto_youtube/db/youtube_nichos.db'
conn = sqlite3.connect(p)
cur = conn.cursor()
cols = [r[1] for r in cur.execute("PRAGMA table_info('resultados')").fetchall()]
print('columns in resultados:', cols)
if 'raw_result' not in cols:
    print('Adding raw_result column...')
    cur.execute("ALTER TABLE resultados ADD COLUMN raw_result TEXT")
    conn.commit()
    print('raw_result added')
else:
    print('raw_result already exists')
conn.close()
