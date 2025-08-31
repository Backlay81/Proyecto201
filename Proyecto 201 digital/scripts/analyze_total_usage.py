"""
Analizador de consumo total de API basado en todos los reportes generados
"""

import os
import re
from datetime import datetime

def analyze_all_reports():
    """Analizar todos los reportes para calcular consumo total"""
    
    print("🔍 ANÁLISIS DE CONSUMO TOTAL - TODAS LAS EJECUCIONES")
    print("=" * 60)
    
    # Directorios a revisar
    base_dir = "C:\\Users\\javie\\AndroidStudioProjects\\Web&Seo"
    project_dir = os.path.join(base_dir, "Proyecto 201 digital")
    
    reports = []
    
    # Buscar reportes en ambos directorios
    for directory in [base_dir, project_dir]:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.startswith("nichos_") and file.endswith(".md"):
                    file_path = os.path.join(directory, file)
                    reports.append(file_path)
    
    # Ordenar por fecha
    reports.sort()
    
    print(f"📄 REPORTES ENCONTRADOS: {len(reports)}")
    print("-" * 40)
    
    total_niches = 0
    total_executions = 0
    total_youtube_units = 0
    total_trends_requests = 0
    
    for report_path in reports:
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer información del reporte
            filename = os.path.basename(report_path)
            
            # Buscar número de nichos analizados
            niches_match = re.search(r'\*\*Nichos analizados:\*\* (\d+)', content)
            niches_count = int(niches_match.group(1)) if niches_match else 0
            
            # Determinar si es sistema con trends o básico
            is_trends = "trends" in filename.lower()
            
            # Calcular consumo estimado
            if is_trends:
                # Sistema ultimate: 3 keywords por defecto en modo testing
                keywords_used = 3
                youtube_units = keywords_used * 101  # 100 search + 1 videos por keyword
                trends_requests = keywords_used  # 1 request por keyword
            else:
                # Sistema básico: keywords del fallback o generadas
                keywords_used = 3  # Estimación conservadora
                youtube_units = keywords_used * 101
                trends_requests = 0
            
            total_niches += niches_count
            total_executions += 1
            total_youtube_units += youtube_units
            total_trends_requests += trends_requests
            
            print(f"📋 {filename}")
            print(f"   📅 Nichos: {niches_count}")
            print(f"   🔧 Tipo: {'Ultimate (Trends)' if is_trends else 'Básico'}")
            print(f"   💰 YouTube estimado: {youtube_units} unidades")
            print(f"   📈 Trends: {trends_requests} requests")
            print()
            
        except Exception as e:
            print(f"❌ Error leyendo {filename}: {e}")
    
    print("=" * 60)
    print("📊 RESUMEN TOTAL:")
    print(f"• Ejecuciones realizadas: {total_executions}")
    print(f"• Nichos analizados: {total_niches}")
    print(f"• YouTube unidades consumidas: {total_youtube_units:,}")
    print(f"• Trends requests: {total_trends_requests} (GRATIS)")
    
    # Calcular porcentajes
    daily_quota = 10000
    percentage_used = (total_youtube_units / daily_quota) * 100
    remaining_units = daily_quota - total_youtube_units
    remaining_analyses = remaining_units // 303  # Asumiendo 303 unidades por análisis
    
    print(f"\n💰 ESTADO DE CUOTA:")
    print(f"• Porcentaje usado: {percentage_used:.1f}%")
    print(f"• Unidades restantes: {remaining_units:,}")
    print(f"• Análisis adicionales posibles: {int(remaining_analyses)}")
    
    if percentage_used > 80:
        print(f"🚨 ALERTA: Has usado más del 80% de tu cuota diaria")
    elif percentage_used > 50:
        print(f"⚠️  CUIDADO: Has usado más del 50% de tu cuota diaria")
    else:
        print(f"✅ ESTADO BUENO: Solo has usado {percentage_used:.1f}% de tu cuota")
    
    print(f"\n📅 FECHA ACTUAL: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 La cuota se renueva cada 24 horas")

if __name__ == "__main__":
    analyze_all_reports()
