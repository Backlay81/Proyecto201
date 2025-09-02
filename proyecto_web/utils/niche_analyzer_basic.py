# Copia local de niche_analyzer_basic.py para proyecto_web
# Nota: simplificada para evitar dependencias cruzadas.
import sys
import os
from pathlib import Path

# Asegurar que las credenciales locales del proyecto sean usadas
sys.path.append(str(Path(__file__).resolve().parents[1] / 'credentials'))
try:
    from config import YOUTUBE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_COUNTRY
except Exception:
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    DEFAULT_LANGUAGE = 'es'
    DEFAULT_COUNTRY = 'ES'

def main():
    print('Analizador local (proyecto_web) - placeholder')
    # Aquí puedes importar o reimplementar la lógica real del analizador.

if __name__ == '__main__':
    main()
