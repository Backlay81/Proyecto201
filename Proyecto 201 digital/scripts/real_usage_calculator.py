"""
Cálculo REAL de consumo de API basado en análisis detallado de reportes
"""

def calculate_real_usage():
    """Calcular el consumo real basado en el análisis detallado de cada reporte"""
    
    print("📊 CÁLCULO REAL DE CONSUMO API - ANÁLISIS DETALLADO")
    print("=" * 65)
    
    # Análisis reporte por reporte basado en los datos reales
    executions = [
        {
            "file": "nichos_analisis_20250828_233854.md",
            "date": "2025-08-28 23:38:54",
            "niches_analyzed": 12,
            "system": "Básico (fallback keywords)",
            "keywords_used": 12,  # Se analizaron 12 nichos diferentes
            "youtube_units": 12 * 101,  # 101 por nicho (100 search + 1 videos)
            "trends_requests": 0
        },
        {
            "file": "nichos_analisis_20250829_002839.md", 
            "date": "2025-08-29 00:28:39",
            "niches_analyzed": 1,
            "system": "Básico (individual)",
            "keywords_used": 1,  # 'mejores seguros para mascotas 2025'
            "youtube_units": 1 * 101,
            "trends_requests": 0
        },
        {
            "file": "nichos_analisis_20250829_003422.md",
            "date": "2025-08-29 00:34:22", 
            "niches_analyzed": 1,
            "system": "Básico (individual)",
            "keywords_used": 1,  # Análisis individual
            "youtube_units": 1 * 101,
            "trends_requests": 0
        },
        {
            "file": "nichos_trends_analisis_20250829_005014.md",
            "date": "2025-08-29 00:50:14",
            "niches_analyzed": 10, 
            "system": "Ultimate (Trends + YouTube)",
            "keywords_used": 10,  # 10 keywords de Google Trends
            "youtube_units": 10 * 101,  # 101 por keyword
            "trends_requests": 10  # 1 request de Trends por keyword
        }
    ]
    
    total_youtube_units = 0
    total_trends_requests = 0
    total_niches = 0
    
    print("📋 DETALLE POR EJECUCIÓN:")
    print("-" * 50)
    
    for i, exec_data in enumerate(executions, 1):
        print(f"{i}. {exec_data['file']}")
        print(f"   📅 Fecha: {exec_data['date']}")
        print(f"   🎯 Nichos: {exec_data['niches_analyzed']}")
        print(f"   🔧 Sistema: {exec_data['system']}")
        print(f"   📊 Keywords usadas: {exec_data['keywords_used']}")
        print(f"   💰 YouTube: {exec_data['youtube_units']} unidades")
        print(f"   📈 Trends: {exec_data['trends_requests']} requests")
        print()
        
        total_youtube_units += exec_data['youtube_units']
        total_trends_requests += exec_data['trends_requests']
        total_niches += exec_data['niches_analyzed']
    
    print("=" * 65)
    print("🏆 TOTALES REALES:")
    print(f"• Ejecuciones: {len(executions)}")
    print(f"• Nichos analizados: {total_niches}")
    print(f"• Keywords procesadas: {sum(ex['keywords_used'] for ex in executions)}")
    print(f"• YouTube unidades: {total_youtube_units:,}")
    print(f"• Trends requests: {total_trends_requests} (GRATIS)")
    
    # Cálculo de estado de cuota
    daily_quota = 10000
    percentage_used = (total_youtube_units / daily_quota) * 100
    remaining_units = daily_quota - total_youtube_units
    
    print(f"\n💰 ESTADO REAL DE CUOTA:")
    print(f"• Cuota diaria: {daily_quota:,} unidades")
    print(f"• Consumidas: {total_youtube_units:,} unidades")
    print(f"• Porcentaje usado: {percentage_used:.2f}%")
    print(f"• Disponibles: {remaining_units:,} unidades")
    
    # Proyecciones
    avg_per_analysis = total_youtube_units / len(executions)
    remaining_analyses = remaining_units // avg_per_analysis
    
    print(f"\n📈 PROYECCIONES:")
    print(f"• Promedio por análisis: {avg_per_analysis:.0f} unidades")
    print(f"• Análisis adicionales posibles: {int(remaining_analyses)}")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if percentage_used < 20:
        print("✅ ESTADO EXCELENTE - Puedes continuar analizando sin problemas")
        print("🚀 Puedes cambiar a modo producción si quieres")
    elif percentage_used < 50:
        print("✅ ESTADO BUENO - Aún tienes margen suficiente")
        print("⚡ Considera mantener el modo testing para optimizar")
    elif percentage_used < 80:
        print("⚠️  CUIDADO - Has usado más de la mitad de tu cuota")
        print("🎯 Mantén el modo testing y planifica el uso restante")
    else:
        print("🚨 ALERTA - Cuota casi agotada")
        print("⏸️  Considera pausar hasta mañana")
    
    return {
        'total_youtube_units': total_youtube_units,
        'total_trends_requests': total_trends_requests,
        'percentage_used': percentage_used,
        'remaining_units': remaining_units
    }

if __name__ == "__main__":
    calculate_real_usage()
