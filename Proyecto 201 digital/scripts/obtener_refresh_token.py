"""
Script para obtener un refresh_token para la API de Google Ads.
Adaptado de: https://github.com/googleads/google-ads-python/blob/master/examples/authentication/authenticate_in_standalone_application.py
"""

import argparse
import sys
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# Los scopes necesarios para la API de Google Ads
SCOPES = ["https://www.googleapis.com/auth/adwords"]

def main(client_secrets_path):
    """Ejecuta el flujo de autenticación para obtener un refresh token."""
    
    credentials = None
    
    # Verificar si el archivo de client_secrets existe
    if not os.path.exists(client_secrets_path):
        print(f"Error: No se encontró el archivo de secretos en {client_secrets_path}")
        print("Debes descargar tu archivo JSON de credenciales desde Google Cloud Console.")
        return
    
    try:
        # Crear el flujo de autenticación
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path, scopes=SCOPES
        )
        
        # Iniciar el flujo de autenticación, abrirá un navegador
        credentials = flow.run_local_server(port=8080)
        
        # Imprimir el refresh token
        print("\n")
        print("="*80)
        print("Tu refresh token es:")
        print(credentials.refresh_token)
        print("="*80)
        print("\nGuarda este token en tu archivo google-ads.yaml")
        
        # Información adicional
        print("\nInformación completa de credenciales:")
        print(f"Token de acceso: {credentials.token}")
        print(f"Token de actualización: {credentials.refresh_token}")
        print(f"Token expira: {credentials.expiry}")
        
    except Exception as e:
        print(f"Error durante la autenticación: {e}")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Obtiene un refresh token para la API de Google Ads."
    )
    parser.add_argument(
        "--client_secrets",
        type=str,
        required=True,
        help="Ruta al archivo JSON de secretos del cliente descargado de Google Cloud Console.",
    )
    args = parser.parse_args()
    
    main(args.client_secrets)
