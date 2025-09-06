# Configuración centralizada de APIs
# Autor: Proyecto 201 digital
# Fecha: 28/08/2025

import os
import sys
from pathlib import Path

# YouTube Data API v3
# Prefer loading from environment (.env) using python-dotenv if available.
try:
	from dotenv import load_dotenv
	_env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
	load_dotenv(_env_path)
except Exception:
	# python-dotenv no está instalado o fallo cargando .env; seguir adelante y usar os.environ
	pass

# Intentar cargar desde .env primero
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

# Si no está en .env, intentar cargar desde credentials/.local_config.py
if not YOUTUBE_API_KEY:
    try:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent
        local_config_path = PROJECT_ROOT / 'credentials' / '.local_config.py'
        if local_config_path.exists():
            # Leer el archivo directamente
            with open(local_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Buscar la línea con YOUTUBE_API_KEY
                for line in content.split('\n'):
                    if line.strip().startswith('YOUTUBE_API_KEY ='):
                        # Extraer el valor entre comillas
                        key_value = line.split('=')[1].strip()
                        if key_value.startswith('"') and key_value.endswith('"'):
                            YOUTUBE_API_KEY = key_value[1:-1]  # Remover comillas
                        elif key_value.startswith("'") and key_value.endswith("'"):
                            YOUTUBE_API_KEY = key_value[1:-1]  # Remover comillas
                        break
            if YOUTUBE_API_KEY and len(YOUTUBE_API_KEY) > 10:
                print("✅ API Key cargada desde credentials/.local_config.py")
    except Exception as e:
        print(f"⚠️  No se pudo cargar API key desde local_config: {e}")

# Google Ads API (se carga desde google-ads.yaml)
# Este archivo complementa las credenciales YAML

# Configuraciones adicionales
PROJECT_ID = "proyecto-digital201"
DEFAULT_LANGUAGE = "es"  # Español
DEFAULT_COUNTRY = "ES"   # España
