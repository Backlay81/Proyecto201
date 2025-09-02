# Configuración centralizada de APIs
# Autor: Proyecto 201 digital
# Fecha: 28/08/2025

import os

# YouTube Data API v3
# Prefer loading from environment (.env) using python-dotenv if available.
try:
	from dotenv import load_dotenv
	_env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
	load_dotenv(_env_path)
except Exception:
	# python-dotenv no está instalado o fallo cargando .env; seguir adelante y usar os.environ
	pass

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', "AIzaSyDBxr4FcogZpngmBVR8EcSpTx8Tz3gcrWc")

# Google Ads API (se carga desde google-ads.yaml)
# Este archivo complementa las credenciales YAML

# Configuraciones adicionales
PROJECT_ID = "proyecto-digital201"
DEFAULT_LANGUAGE = "es"  # Español
DEFAULT_COUNTRY = "ES"   # España
