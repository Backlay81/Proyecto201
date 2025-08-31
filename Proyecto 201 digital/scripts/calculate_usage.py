"""
Calculadora de consumo de API sin dependencias externas
"""

def calculate_api_usage():
    """Calcular consumo estimado basado en nuestra configuración"""
    
    print("💰 CALCULADORA DE CONSUMO API - YOUTUBE")
    print("=" * 50)
    
    # Costos conocidos de YouTube API v3
    search_cost = 100  # unidades por search.list()
    videos_cost = 1    # unidades por videos.list()
    daily_quota = 10000  # cuota gratuita diaria
    
    print("📊 COSTOS UNITARIOS:")
    print(f"• search.list() = {search_cost} unidades")
    print(f"• videos.list() = {videos_cost} unidades")
    print(f"• Por keyword = {search_cost + videos_cost} unidades")
    print(f"• Cuota diaria gratuita = {daily_quota:,} unidades")
    
    # Configuración actual (modo testing)
    testing_keywords = 3
    production_keywords = 10
    
    print(f"\n🧪 MODO TESTING (configuración actual):")
    testing_total = testing_keywords * (search_cost + videos_cost)
    testing_percentage = (testing_total / daily_quota) * 100
    
    print(f"• Keywords: {testing_keywords}")
    print(f"• Consumo total: {testing_total} unidades")
    print(f"• Porcentaje de cuota: {testing_percentage:.1f}%")
    print(f"• Quedan disponibles: {daily_quota - testing_total:,} unidades")
    print(f"• Análisis adicionales posibles: {(daily_quota - testing_total) // testing_total}")
    
    print(f"\n🚀 MODO PRODUCCIÓN (cuando activemos):")
    production_total = production_keywords * (search_cost + videos_cost)
    production_percentage = (production_total / daily_quota) * 100
    
    print(f"• Keywords: {production_keywords}")
    print(f"• Consumo total: {production_total} unidades")
    print(f"• Porcentaje de cuota: {production_percentage:.1f}%")
    print(f"• Quedan disponibles: {daily_quota - production_total:,} unidades")
    print(f"• Análisis adicionales posibles: {(daily_quota - production_total) // production_total}")
    
    # Estimación de uso previo
    print(f"\n📈 ESTIMACIÓN BASADA EN REPORTES:")
    print("• Última ejecución: 1 nicho analizado")
    print("• Probablemente usó: ~303 unidades (3 keywords)")
    print("• Quedan aproximadamente: ~9,697 unidades")
    
    print(f"\n⚠️  RECOMENDACIONES:")
    print("• Modo testing es muy seguro (solo 3% de cuota)")
    print("• Puedes ejecutar 32+ análisis en modo testing")
    print("• Para producción, 9 análisis por día serían el máximo")
    print("• Google Trends es GRATIS (no consume cuota)")
    
    # Información adicional
    print(f"\n🔍 PARA VERIFICAR CONSUMO REAL:")
    print("• Ve a: https://console.cloud.google.com/")
    print("• APIs & Services > Quotas")
    print("• Busca: YouTube Data API v3")
    print("• Verás: 'Queries per day' usado/disponible")

if __name__ == "__main__":
    calculate_api_usage()
