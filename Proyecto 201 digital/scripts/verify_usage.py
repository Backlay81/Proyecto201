"""
Enlaces y métodos para verificar consumo real de API
"""

def show_verification_methods():
    """Mostrar diferentes formas de verificar el consumo de API"""
    
    print("🔍 MÉTODOS PARA VERIFICAR CONSUMO REAL DE API")
    print("=" * 60)
    
    print("1️⃣ GOOGLE CLOUD CONSOLE (Método más preciso):")
    print("   📧 Cuenta: javie@proyecto201digital.com") 
    print("   🌐 URL: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas")
    print("   📊 Buscar: 'Queries per day' en YouTube Data API v3")
    print("   💡 Aquí verás exactamente cuántas unidades has usado hoy")
    
    print("\n2️⃣ GOOGLE DEVELOPERS CONSOLE:")
    print("   🌐 URL: https://console.developers.google.com/apis/api/youtube.googleapis.com/quotas")
    print("   📈 Métricas: Requests per day, Per-user quota")
    
    print("\n3️⃣ BASADO EN NUESTROS REGISTROS:")
    print("   📅 Última ejecución: 2025-08-29 00:28:39")
    print("   🎯 Nicho analizado: 'mejores seguros para mascotas 2025'")
    print("   💰 Estimación: ~303 unidades (3 keywords en modo testing)")
    
    print("\n4️⃣ CONFIGURACIÓN ACTUAL DEL SISTEMA:")
    print("   🧪 Modo: TESTING")
    print("   📊 Límite diario YouTube: 20 requests")
    print("   📈 Límite diario Trends: 10 requests")
    print("   🔢 Keywords por análisis: 3")
    print("   ⚡ Consumo por análisis: ~303 unidades")
    
    print("\n📱 RESUMEN EJECUTIVO:")
    print("   ✅ Has usado aproximadamente: 303 unidades")
    print("   💰 Te quedan aproximadamente: 9,697 unidades")
    print("   🔥 Porcentaje usado: 3.0% de tu cuota diaria")
    print("   🚀 Análisis adicionales posibles: 32+")
    
    print("\n⚠️  NOTAS IMPORTANTES:")
    print("   • Google Trends es completamente GRATIS")
    print("   • Solo YouTube Data API consume cuota")
    print("   • Cuota se resetea cada 24 horas (zona horaria del proyecto)")
    print("   • Modo testing usa solo 3% de cuota diaria")

if __name__ == "__main__":
    show_verification_methods()
