# Configuración específica para YouTube Nichos Analyzer
# =====================================================

import os
import sys

# Añadir el directorio de configuración al path
sys.path.append(os.path.dirname(__file__))

# Importar configuración base si existe
try:
    from config import YOUTUBE_API_KEY, PROJECT_ID, DEFAULT_LANGUAGE, DEFAULT_COUNTRY
except ImportError:
    # Configuración por defecto si no existe config.py
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    PROJECT_ID = "nichos-youtube-analyzer"
    DEFAULT_LANGUAGE = "es"
    DEFAULT_COUNTRY = "ES"

# Configuraciones específicas para YouTube
YOUTUBE_CONFIG = {
    'api_key': YOUTUBE_API_KEY,
    'max_results': 50,
    'days_back': 365,
    'quota_limit': 10000,
    'search_cost': 100,
    'details_cost': 1
}

# Configuraciones de análisis
ANALYSIS_CONFIG = {
    'monetizable_threshold': 10000,
    'automation_threshold': 0.3,
    'low_saturation_threshold': 10,
    'high_saturation_threshold': 25
}

# Pesos para scoring
SCORING_WEIGHTS = {
    'views': 0.4,
    'monetizable': 0.4,
    'saturation': 0.2
}

# Configuraciones de output
OUTPUT_CONFIG = {
    'formats': ['csv', 'parquet'],
    'timezone': 'Europe/Madrid',
    'date_format': '%Y-%m-%d %H:%M:%S'
}
