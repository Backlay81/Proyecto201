# Proyecto Web - credentials/config.py (template)
# Copia este archivo y completa YOUTUBE_API_KEY si necesitas usar la API.
import os

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
PROJECT_ID = os.environ.get('PROJECT_ID', 'proyecto_web')
DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'es')
DEFAULT_COUNTRY = os.environ.get('DEFAULT_COUNTRY', 'ES')
