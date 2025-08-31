"""
Análisis OFICIAL del consumo real basado en Google Cloud Console
"""

def analyze_official_usage():
    """Analizar el consumo real según los datos oficiales de Google Cloud Console"""
    
    print("🌐 DATOS OFICIALES - GOOGLE CLOUD CONSOLE")
    print("=" * 55)
    
    # Datos reales de Google Cloud Console
    daily_quota = 10000
    current_usage = 4543
    usage_percentage = 45.43
    remaining_units = daily_quota - current_usage
    
    print("📊 ESTADO OFICIAL ACTUAL:")
    print(f"• Cuota diaria total: {daily_quota:,} unidades")
    print(f"• Consumo actual: {current_usage:,} unidades")
    print(f"• Porcentaje usado: {usage_percentage}%")
    print(f"• Unidades disponibles: {remaining_units:,} unidades")
    
    # Comparación con nuestra estimación
    our_estimate = 2424
    difference = current_usage - our_estimate
    
    print(f"\n🔍 COMPARACIÓN CON NUESTRA ESTIMACIÓN:")
    print(f"• Nuestra estimación: {our_estimate:,} unidades")
    print(f"• Consumo real: {current_usage:,} unidades")
    print(f"• Diferencia: +{difference:,} unidades")
    print(f"• Precisión estimación: {(our_estimate/current_usage)*100:.1f}%")
    
    # Análisis de la diferencia
    print(f"\n💡 EXPLICACIÓN DE LA DIFERENCIA:")
    print("• Nuestro cálculo: 24 nichos × 101 unidades = 2,424")
    print("• Consumo real: 4,543 unidades")
    print("• Diferencia de +2,119 unidades sugiere:")
    print("  - Más requests de los estimados")
    print("  - Posibles reintetos automáticos")
    print("  - Análisis adicionales no registrados")
    print("  - Videos.list con más resultados")
    
    # Cálculo de consumo por análisis real
    total_analyses = 4  # Sabemos que hicimos 4 ejecuciones
    real_avg_per_analysis = current_usage / total_analyses
    
    print(f"\n📈 CONSUMO REAL PROMEDIO:")
    print(f"• Ejecuciones realizadas: {total_analyses}")
    print(f"• Promedio real: {real_avg_per_analysis:.0f} unidades/análisis")
    print(f"• Estimado era: 606 unidades/análisis")
    print(f"• Factor real: {real_avg_per_analysis/606:.1f}x más alto")
    
    # Proyecciones con datos reales
    remaining_analyses = remaining_units / real_avg_per_analysis
    
    print(f"\n🚀 PROYECCIONES CON DATOS REALES:")
    print(f"• Análisis adicionales posibles: {int(remaining_analyses)}")
    print(f"• Unidades por análisis (real): ~{real_avg_per_analysis:.0f}")
    
    # Estado y recomendaciones
    print(f"\n💰 ESTADO ACTUAL:")
    if usage_percentage > 80:
        status = "🚨 CRÍTICO"
        recommendation = "Pausar análisis hasta mañana"
    elif usage_percentage > 60:
        status = "⚠️  ALTO CONSUMO"
        recommendation = "Máximo 2-3 análisis más"
    elif usage_percentage > 40:
        status = "🔶 CONSUMO MODERADO"
        recommendation = "Continuar con precaución, 4-5 análisis más"
    else:
        status = "✅ ESTADO BUENO"
        recommendation = "Puedes continuar normalmente"
    
    print(f"• Estado: {status}")
    print(f"• Recomendación: {recommendation}")
    
    # Optimizaciones sugeridas
    print(f"\n🔧 OPTIMIZACIONES RECOMENDADAS:")
    print("• Reducir maxResults en búsquedas de YouTube")
    print("• Implementar análisis batch (varios nichos en 1 request)")
    print("• Usar más el sistema de fallback (sin YouTube)")
    print("• Activar logs detallados para tracking preciso")
    
    # Cuándo se renueva la cuota
    print(f"\n🕐 RENOVACIÓN DE CUOTA:")
    print("• La cuota se renueva cada 24 horas")
    print("• Zona horaria del proyecto: UTC")
    print("• Próxima renovación: ~medianoche UTC")
    
    return {
        'official_usage': current_usage,
        'remaining_units': remaining_units,
        'usage_percentage': usage_percentage,
        'real_avg_per_analysis': real_avg_per_analysis,
        'remaining_analyses': int(remaining_analyses)
    }

if __name__ == "__main__":
    result = analyze_official_usage()
    
    print(f"\n" + "="*55)
    print("🎯 RESUMEN EJECUTIVO:")
    print(f"• Has usado {result['usage_percentage']}% de tu cuota diaria")
    print(f"• Te quedan {result['remaining_units']:,} unidades")
    print(f"• Puedes hacer ~{result['remaining_analyses']} análisis más")
    print(f"• Consumo real promedio: {result['real_avg_per_analysis']:.0f} unidades/análisis")
