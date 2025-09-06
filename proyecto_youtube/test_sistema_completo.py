#!/usr/bin/env python3
"""
test_sistema_completo.py
Test completo del sistema profesionalizado
Verifica: dependencias, DB, exports, Rich, Polars
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configurar paths
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / 'config'))
sys.path.append(str(PROJECT_ROOT / 'utils'))

def test_dependencias():
    """Test 1: Verificar dependencias instaladas"""
    print("🔍 TEST 1: Verificando dependencias...")

    deps_status = {
        'polars': False,
        'rich': False,
        'sqlalchemy': False,
        'pandas': False,
        'google_api': False
    }

    try:
        import polars as pl
        print(f"✅ Polars: {pl.__version__}")
        deps_status['polars'] = True
    except ImportError:
        print("❌ Polars no instalado")

    try:
        from rich.console import Console
        console = Console()
        console.print("✅ Rich funcionando", style="bold green")
        deps_status['rich'] = True
    except ImportError:
        print("❌ Rich no instalado")

    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
        deps_status['sqlalchemy'] = True
    except ImportError:
        print("❌ SQLAlchemy no instalado")

    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
        deps_status['pandas'] = True
    except ImportError:
        print("❌ Pandas no instalado")

    try:
        from googleapiclient.discovery import build
        print("✅ Google API Client funcionando")
        deps_status['google_api'] = True
    except ImportError:
        print("❌ Google API Client no instalado")

    return deps_status

def test_config():
    """Test 2: Verificar configuración"""
    print("\n🔍 TEST 2: Verificando configuración...")

    try:
        # Buscar en múltiples ubicaciones
        api_key = None
        config_paths = [
            PROJECT_ROOT / 'config' / 'config.py',
            PROJECT_ROOT / 'nichos_youtube' / 'config.py',
            PROJECT_ROOT / 'canales_youtube' / 'config.py'
        ]

        for config_path in config_paths:
            if config_path.exists():
                sys.path.insert(0, str(config_path.parent))
                try:
                    from config import YOUTUBE_API_KEY
                    api_key = YOUTUBE_API_KEY
                    break
                except ImportError:
                    continue

        # También buscar en variables de entorno
        if not api_key:
            api_key = os.environ.get('YOUTUBE_API_KEY')

        if api_key and len(api_key) > 10:
            print("✅ YOUTUBE_API_KEY configurada")
            return True
        else:
            print("❌ YOUTUBE_API_KEY no encontrada o inválida")
            return False
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
        return False

def test_db():
    """Test 3: Verificar base de datos"""
    print("\n🔍 TEST 3: Verificando base de datos...")

    try:
        # Verificar que existe la DB
        db_file = PROJECT_ROOT / 'db' / 'youtube_nichos.db'
        if db_file.exists():
            print("✅ Archivo de base de datos encontrado")
            return True
        else:
            print("❌ Archivo de base de datos no encontrado")
            return False

    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def test_exports():
    """Test 4: Verificar exports"""
    print("\n🔍 TEST 4: Verificando exports...")

    test_data = [
        {'keyword': 'test1', 'score': 85, 'videos': 50},
        {'keyword': 'test2', 'score': 92, 'videos': 45}
    ]

    try:
        # Test CSV con Polars
        import polars as pl
        df = pl.DataFrame(test_data)
        test_csv = PROJECT_ROOT / 'test_output.csv'
        df.write_csv(test_csv)
        print("✅ Export CSV con Polars funcionando")

        # Test Parquet
        test_parquet = PROJECT_ROOT / 'test_output.parquet'
        df.write_parquet(test_parquet)
        print("✅ Export Parquet funcionando")

        # Limpiar archivos de test
        test_csv.unlink(missing_ok=True)
        test_parquet.unlink(missing_ok=True)

        return True

    except Exception as e:
        print(f"❌ Error en exports: {e}")
        return False

def test_scripts_basic():
    """Test 5: Verificar que los scripts existen"""
    print("\n🔍 TEST 5: Verificando scripts...")

    try:
        # Test nichos_youtube
        nichos_file = PROJECT_ROOT / 'nichos_youtube' / 'nichos_youtube.py'
        if nichos_file.exists():
            with open(nichos_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'NicheAnalyzerYouTubeUnificado' in content:
                    print("✅ nichos_youtube.py existe y contiene la clase principal")
                else:
                    print("❌ nichos_youtube.py no contiene la clase esperada")
                    return False
        else:
            print("❌ nichos_youtube.py no encontrado")
            return False

        # Test buscar_canales
        canales_file = PROJECT_ROOT / 'canales_youtube' / 'buscar_canales_youtube.py'
        if canales_file.exists():
            with open(canales_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'def main' in content:
                    print("✅ buscar_canales_youtube.py existe y contiene función main")
                else:
                    print("❌ buscar_canales_youtube.py no contiene función main")
                    return False
        else:
            print("❌ buscar_canales_youtube.py no encontrado")
            return False

        return True

    except Exception as e:
        print(f"❌ Error verificando scripts: {e}")
        return False

def test_api_connection(api_key):
    """Test 6: Verificar conexión a YouTube API (opcional)"""
    print("\n🔍 TEST 6: Verificando conexión API...")

    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Test simple search
        request = youtube.search().list(
            q='test',
            part='id',
            type='video',
            maxResults=1
        )
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            print("✅ Conexión a YouTube API funcionando")
            return True
        else:
            print("❌ Respuesta API vacía")
            return False

    except Exception as e:
        print(f"❌ Error en conexión API: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO TEST COMPLETO DEL SISTEMA")
    print("=" * 50)

    results = {}

    # Test 1: Dependencias
    results['dependencias'] = test_dependencias()

    # Test 2: Configuración
    results['config'] = test_config()

    # Test 3: Base de datos
    results['db'] = test_db()

    # Test 4: Exports
    results['exports'] = test_exports()

    # Test 5: Scripts
    results['scripts'] = test_scripts_basic()

    # Test 6: API (solo si hay API key)
    try:
        from config import YOUTUBE_API_KEY
        if YOUTUBE_API_KEY:
            results['api'] = test_api_connection(YOUTUBE_API_KEY)
        else:
            results['api'] = False
            print("\n⚠️  Saltando test API (no hay API key)")
    except:
        results['api'] = False
        print("\n⚠️  Saltando test API (error importando API key)")

    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DEL TEST:")

    passed = 0
    total = len(results)

    for test_name, status in results.items():
        if isinstance(status, dict):
            # Para dependencias, contar cuántas pasaron
            deps_passed = sum(1 for v in status.values() if v)
            deps_total = len(status)
            print(f"   {test_name.capitalize()}: {deps_passed}/{deps_total} ✅")
            if deps_passed == deps_total:
                passed += 1
        else:
            status_icon = "✅" if status else "❌"
            print(f"   {test_name.capitalize()}: {status_icon}")
            if status:
                passed += 1

    print(f"\n🎯 Tests pasados: {passed}/{total}")

    if passed == total:
        print("🎉 ¡TODOS LOS TESTS PASARON! El sistema está listo.")
        return True
    elif passed >= total - 1:
        print("⚠️  Casi todos los tests pasaron. Sistema funcional.")
        return True
    else:
        print("❌ Algunos tests fallaron. Revisar configuración.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
