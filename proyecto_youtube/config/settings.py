# Configuración para YouTube Nichos Analyzer
# ===========================================

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# YouTube Data API v3
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Configuraciones del análisis
DEFAULT_MAX_RESULTS = 50
DEFAULT_DAYS_BACK = 365
API_QUOTA_LIMIT = 10000
SEARCH_COST = 100  # Unidades por búsqueda
DETAILS_COST = 1   # Unidades por video

# Configuraciones de análisis
MONETIZABLE_THRESHOLD = 10000  # Views mínimas para considerar monetizable
AUTOMATION_THRESHOLD = 0.3     # Ratio mínimo para considerar automatizable
LOW_SATURATION_THRESHOLD = 10  # Máximo resultados para baja saturación
HIGH_SATURATION_THRESHOLD = 25 # Mínimo resultados para alta saturación

# Configuraciones de scoring
WEIGHTS = {
    'views': 0.4,
    'monetizable': 0.4,
    'saturation': 0.2
}

# Configuraciones de exportación
OUTPUT_FORMATS = ['csv', 'parquet']
TIMEZONE = 'Europe/Madrid'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'nichos_youtube.log'
