"""
Script de Instalación Automática
Proyecto 201 digital - Sistema de Análisis de Nichos
Fecha: 28/08/2025
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Detalles: {e.stderr}")
        return False

def main():
    print("🚀 INSTALACIÓN DEL SISTEMA DE ANÁLISIS DE NICHOS")
    print("=" * 60)

    # Verificar Python
    print(f"🐍 Python version: {sys.version}")

    # Instalar dependencias
    if run_command("pip install -r requirements.txt", "Instalando dependencias desde requirements.txt"):
        print("\n📦 Dependencias instaladas:")
        print("   ✅ google-api-python-client")
        print("   ✅ pytrends")
        print("   ✅ pandas")
        print("   ✅ requests")
        print("   ✅ python-dotenv")

    # Verificar instalación
    print("\n🔍 Verificando instalación...")
    try:
        import pytrends
        print("✅ pytrends instalado correctamente")
    except ImportError:
        print("❌ Error: pytrends no se instaló correctamente")

    try:
        from googleapiclient.discovery import build
        print("✅ google-api-python-client instalado correctamente")
    except ImportError:
        print("❌ Error: google-api-python-client no se instaló correctamente")

    # Crear directorio de logs si no existe
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print("✅ Directorio de logs creado")

    print("\n" + "=" * 60)
    print("🎯 INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Verificar que la API key de YouTube esté configurada en credentials/config.py")
    print("2. Ejecutar: python scripts/niche_analyzer.py")
    print("3. Revisar el reporte generado")

    print("\n💡 COMANDOS ÚTILES:")
    print("   📊 Ejecutar análisis: python scripts/niche_analyzer.py")
    print("   🔍 Probar YouTube API: python scripts/youtube_search.py")
    print("   📈 Ver documentación: README.md")

if __name__ == "__main__":
    main()
