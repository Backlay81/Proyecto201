"""
Script para verificar el consumo de unidades de la API de YouTube
"""

import sys
import os
from datetime import datetime

# Agregar el directorio credentials al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'credentials'))

try:
    from googleapiclient.discovery import build
    from config import YOUTUBE_API_KEY
    
    def check_youtube_quota():
        """Verificar información de cuota de YouTube API"""
        print("🔍 VERIFICANDO CONSUMO DE API YOUTUBE")
        print("=" * 50)
        
        # Información de configuración actual
        print("📋 CONFIGURACIÓN ACTUAL:")
        print(f"• API Key configurada: {'✅ Sí' if YOUTUBE_API_KEY and YOUTUBE_API_KEY != 'tu_api_key_aqui' else '❌ No'}")
        
        # Costos conocidos de YouTube API v3
        print("\n💰 COSTOS YOUTUBE API v3:")
        print("• search.list() = 100 unidades por request")
        print("• videos.list() = 1 unidad por request")
        print("• Cuota diaria gratuita = 10,000 unidades")
        print("• Cuota por proyecto = 1,000,000 unidades/día (si se paga)")
        
        # Cálculo de nuestro sistema
        print("\n🧮 CÁLCULO NUESTRO SISTEMA:")
        print("• Modo TESTING: 3 keywords máximo")
        print("• Por keyword: 1 search.list (100) + 1 videos.list (1) = 101 unidades")
        print("• Total modo testing: 3 × 101 = 303 unidades máximo")
        print("• Porcentaje de cuota gratuita: 303/10,000 = 3.03%")
        
        print("\n🔥 MODO PRODUCCIÓN (si activamos):")
        print("• 10-12 keywords: 10 × 101 = 1,010 unidades")
        print("• Porcentaje de cuota gratuita: 1,010/10,000 = 10.1%")
        
        # Test básico de conectividad
        try:
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            
            # Hacer un request muy pequeño para probar
            print("\n🧪 TEST DE CONECTIVIDAD:")
            request = youtube.search().list(
                part='snippet',
                q='test',
                maxResults=1,
                type='video'
            )
            response = request.execute()
            
            if response.get('items'):
                print("✅ API funciona correctamente")
                print("💡 Este test consumió ~100 unidades")
            else:
                print("⚠️  API responde pero sin resultados")
                
        except Exception as e:
            print(f"❌ Error en API: {e}")
            if "quotaExceeded" in str(e):
                print("🚨 CUOTA EXCEDIDA - Has alcanzado el límite diario")
            elif "forbidden" in str(e).lower():
                print("🚨 ACCESO DENEGADO - Verifica la API Key")
                
        # Estimación para hoy
        print(f"\n📅 ESTIMACIÓN PARA HOY ({datetime.now().strftime('%Y-%m-%d')}):")
        print("• Si ejecutas modo testing: ~303 unidades")
        print("• Quedarían disponibles: ~9,697 unidades")
        print("• Podrías ejecutar: ~32 análisis más en modo testing")
        
    if __name__ == "__main__":
        check_youtube_quota()
        
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("💡 Ejecuta: pip install google-api-python-client")
except Exception as e:
    print(f"❌ Error general: {e}")
