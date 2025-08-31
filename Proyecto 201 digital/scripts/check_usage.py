"""
Script para consultar el estado actual de consumo de API en tiempo real
"""

from api_usage_tracker import show_current_usage, tracker
from datetime import datetime

def main():
    """Mostrar estado completo del consumo de API"""
    
    print("🔍 ESTADO ACTUAL DE CONSUMO API")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Mostrar estado actual
    show_current_usage()
    
    # Información adicional
    status = tracker.get_current_status()
    
    print(f"\n💡 INFORMACIÓN ADICIONAL:")
    print(f"• La cuota se resetea a las 00:00 UTC")
    print(f"• Google Trends es completamente GRATIS")
    print(f"• Solo YouTube Data API consume cuota")
    
    # Alertas
    if status['percentage_used'] > 80:
        print(f"\n🚨 ALERTA CRÍTICA:")
        print(f"• Has superado el 80% de tu cuota diaria")
        print(f"• Considera pausar hasta mañana")
    elif status['percentage_used'] > 60:
        print(f"\n⚠️  ADVERTENCIA:")
        print(f"• Has superado el 60% de tu cuota diaria")
        print(f"• Planifica cuidadosamente el uso restante")
    elif status['percentage_used'] > 40:
        print(f"\n📊 ESTADO MODERADO:")
        print(f"• Vas por buen camino, controla el uso")
    else:
        print(f"\n✅ ESTADO EXCELENTE:")
        print(f"• Tienes mucho margen para continuar")

if __name__ == "__main__":
    main()
