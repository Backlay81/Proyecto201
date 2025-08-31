"""
Script de Prueba Rápida
Verifica que todas las dependencias y APIs estén funcionando
Proyecto 201 digital - Opción A
Fecha: 28/08/2025
"""

import sys
import os

def test_imports():
    """Probar imports de dependencias"""
    print("🔍 Probando imports de dependencias...")

    try:
        from pytrends.request import TrendReq
        print("✅ pytrends importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando pytrends: {e}")
        return False

    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        print("✅ google-api-python-client importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando google-api-python-client: {e}")
        return False

    try:
        import pandas as pd
        print("✅ pandas importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando pandas: {e}")
        return False

    return True

def test_config():
    """Probar configuración"""
    print("\n🔍 Probando configuración...")

    try:
        # Añadir la carpeta credentials al path
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
        from config import YOUTUBE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_COUNTRY
        print("✅ Configuración importada correctamente")
        print(f"   📍 País: {DEFAULT_COUNTRY}")
        print(f"   🌐 Idioma: {DEFAULT_LANGUAGE}")

        if YOUTUBE_API_KEY and YOUTUBE_API_KEY != "tu_api_key_aqui":
            print("✅ YouTube API Key configurada")
        else:
            print("⚠️  YouTube API Key no configurada o es placeholder")

        return True
    except ImportError as e:
        print(f"❌ Error importando configuración: {e}")
        return False

def test_youtube_api():
    """Probar YouTube API con una consulta simple"""
    print("\n🔍 Probando YouTube Data API...")

    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
        from config import YOUTUBE_API_KEY

        if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "tu_api_key_aqui":
            print("⚠️  Saltando test de YouTube API - API Key no configurada")
            return True

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Consulta simple de prueba
        request = youtube.search().list(
            q="test",
            part="snippet",
            type="video",
            maxResults=1
        )
        response = request.execute()

        if response['items']:
            print("✅ YouTube API funcionando correctamente")
            print(f"   📹 Video de prueba encontrado: {response['items'][0]['snippet']['title'][:50]}...")
            return True
        else:
            print("⚠️  YouTube API respondió pero sin resultados")
            return True

    except HttpError as e:
        if e.resp.status == 403:
            print("❌ Error de autenticación en YouTube API - Verificar API Key")
        else:
            print(f"❌ Error en YouTube API: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en YouTube API: {e}")
        return False

def test_trends_api():
    """Probar Google Trends API"""
    print("\n🔍 Probando Google Trends API...")

    try:
        from pytrends.request import TrendReq
        import pandas as pd

        pytrends = TrendReq(hl='es', tz=360)

        # Consulta simple de prueba
        pytrends.build_payload(kw_list=["python"], timeframe="now 1-d")
        trends_data = pytrends.interest_over_time()

        if not trends_data.empty:
            print("✅ Google Trends API funcionando correctamente")
            print(f"   📈 Datos obtenidos para 'python': {len(trends_data)} registros")
            return True
        else:
            print("⚠️  Google Trends API respondió pero sin datos históricos")
            return True

    except Exception as e:
        print(f"❌ Error en Google Trends API: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBA RÁPIDA DEL SISTEMA DE ANÁLISIS DE NICHOS")
    print("=" * 60)

    tests_passed = 0
    total_tests = 4

    # Test 1: Imports
    if test_imports():
        tests_passed += 1

    # Test 2: Configuración
    if test_config():
        tests_passed += 1

    # Test 3: YouTube API
    if test_youtube_api():
        tests_passed += 1

    # Test 4: Google Trends
    if test_trends_api():
        tests_passed += 1

    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Tests pasados: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
        print("\n🚀 Puedes ejecutar el análisis completo:")
        print("   python scripts/niche_analyzer.py")
    elif tests_passed >= 2:
        print("⚠️  Sistema parcialmente funcional. Revisa las configuraciones.")
        print("\n🔧 Posibles soluciones:")
        print("   - Instalar dependencias: pip install -r requirements.txt")
        print("   - Configurar YouTube API Key en credentials/config.py")
        print("   - Verificar conexión a internet")
    else:
        print("❌ Sistema no funcional. Revisa la instalación.")

    print("\n💡 Para más ayuda: README.md")

if __name__ == "__main__":
    main()
