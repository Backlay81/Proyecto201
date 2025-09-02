# Configuración específica para Web Nichos Analyzer
# ==================================================

import os
import sys

# Configuraciones de Google Ads (cuando esté disponible)
GOOGLE_ADS_CONFIG = {
    'config_file': 'config/google-ads.yaml',
    'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', ''),
    'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID', ''),
    'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET', ''),
    'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN', ''),
    'customer_id': os.getenv('GOOGLE_ADS_CUSTOMER_ID', '')
}

# Configuraciones de Google Trends
TRENDS_CONFIG = {
    'language': 'es-ES',
    'timezone': 360,
    'timeframe': 'today 12-m',
    'geo': 'ES'
}

# Configuraciones de análisis web
ANALYSIS_CONFIG = {
    'min_search_volume': 1000,
    'max_cpc': 5.0,
    'max_competition': 0.8,
    'trend_threshold': 0.1
}

# Pesos para scoring web
SCORING_WEIGHTS = {
    'volume': 0.4,
    'cpc': 0.2,
    'competition': 0.3,
    'trend': 0.1
}

# Configuraciones de simulación (hasta que Google Ads esté disponible)
SIMULATION_CONFIG = {
    'enabled': True,
    'volume_range': (1000, 100000),
    'cpc_range': (0.1, 5.0),
    'competition_range': (0.0, 1.0)
}

# Configuraciones de output
OUTPUT_CONFIG = {
    'formats': ['csv', 'parquet'],
    'timezone': 'Europe/Madrid',
    'date_format': '%Y-%m-%d %H:%M:%S'
}
