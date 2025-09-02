"""
Sistema Automatizado de Análisis de Nichos Rentables - Versión Mejorada
Con normalización, automatización, filtros de fecha y monetización
Proyecto 201 digital - Opción A
Fecha: 28/08/2025
"""

import sys
import os
import time
import random
import csv
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Añadir la carpeta credentials al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
from config import YOUTUBE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_COUNTRY


class NicheAnalyzerEnhanced:
    """
    Sistema mejorado para encontrar nichos rentables en YouTube
    Con normalización, automatización, filtros y monetización
    """

    def __init__(self):
        """Inicializar el analizador con configuraciones optimizadas"""
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Configuración para límites de API (Opción A)
        self.daily_youtube_quota = 10000  # Unidades por día
        self.daily_youtube_requests = 0
        self.max_youtube_per_day = 100  # Límite conservador

        # Fecha límite para contenido reciente (últimos 12 meses)
        self.date_limit = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Keywords predefinidos para análisis (sin Trends)
        self.predefined_keywords = [
            # Finanzas y dinero
            "finanzas personales", "invertir dinero", "ahorrar dinero", "presupuesto mensual",
            "educación financiera", "inversiones seguras", "criptomonedas para principiantes",

            # Tecnología y programación
            "aprender python", "desarrollo web", "inteligencia artificial", "machine learning",
            "programación para principiantes", "desarrollo móvil", "ciberseguridad",

            # Salud y bienestar
            "ejercicios en casa", "meditación diaria", "alimentación saludable",
            "perder peso", "rutina de ejercicios", "bienestar mental",

            # Negocios y emprendimiento
            "emprender desde cero", "marketing digital", "ecommerce", "dropshipping",
            "freelancer", "negocio online", "startups",

            # Estilo de vida
            "productividad", "organización del hogar", "cocina fácil",
            "viajes baratos", "decoración del hogar", "jardinería",

            # Educación y aprendizaje
            "idiomas gratis", "certificaciones online", "cursos gratuitos",
            "estudiar desde casa", "desarrollo personal"
        ]

        # Categorías de monetización por nicho
        self.monetization_categories = {
            # Muy Alto Potencial
            "finanzas": "Muy Alto", "cripto": "Muy Alto", "invertir": "Muy Alto",
            "trading": "Muy Alto", "forex": "Muy Alto", "bolsa": "Muy Alto",

            # Alto Potencial
            "programación": "Alto", "python": "Alto", "desarrollo": "Alto",
            "tecnología": "Alto", "marketing": "Alto", "negocios": "Alto",

            # Medio Potencial
            "salud": "Medio", "fitness": "Medio", "educación": "Medio",
            "aprendizaje": "Medio", "productividad": "Medio",

            # Bajo Potencial
            "vlogs": "Bajo", "gaming": "Bajo", "entretenimiento": "Bajo",
            "música": "Bajo", "viajes": "Bajo"
        }

    def clasificar_monetizacion(self, keyword):
        """
        🔥 MEJORA: Clasificación avanzada del tipo de monetización
        Detecta el modelo de monetización más efectivo por keyword
        Prioriza anuncios (CPM alto) sobre afiliación
        """
        keyword_lower = keyword.lower()
        
        # 🔗 Palabras clave para AFILIACIÓN (productos físicos, comparativas)
        afiliacion = [
            "comprar", "mejores", "review", "productos", "comparativa", "guía",
            "precio", "barato", "amazon", "oferta", "ranking", "pienso", 
            "juguetes", "accesorios", "snacks", "alimentación", "recomendación", 
            "top", "análisis", "prueba", "características", "modelos"
        ]
        
        # 💰 Palabras clave para ANUNCIOS (CPM alto, servicios financieros amplios)
        anuncios = [
            "finanzas", "financiero", "financiera", "financieros", "invertir", 
            "inversión", "trading", "seguros", "banca", "abogado", "consultoría", 
            "marketing", "coaching", "educación", "psicología", "cuenta", "cuentas", 
            "remunerada", "remuneradas", "interés", "ahorros", "cuenta bancaria", 
            "cuenta sin comisiones", "forex", "bolsa", "préstamos", "tarjetas", 
            "banco", "cripto", "criptomonedas", "emprendimiento"
        ]
        
        # Detectar presencia de cada tipo
        tiene_afiliacion = any(word in keyword_lower for word in afiliacion)
        tiene_anuncios = any(word in keyword_lower for word in anuncios)
        
        # 🎯 Clasificar según combinación (prioriza anuncios por CPM más alto)
        if tiene_afiliacion and tiene_anuncios:
            return "Afiliación + Anuncios"
        elif tiene_anuncios:
            return "Solo Anuncios"
        elif tiene_afiliacion:
            return "Solo Afiliación"
        else:
            return "Difícil Monetizar"

    def is_automatizable(self, keyword):
        """
        🔥 MEJORA: Detectar si un nicho es automatizable con IA
        Lista ampliada con nichos de productos y contenido estructurado
        """
        # 🤖 Combinación de keywords actuales + propuestas mejoradas
        automatizable_keywords = [
            # Keywords originales (contenido estructurado)
            "review", "top", "mejores", "comparativa", "tutorial", "guía",
            "ranking", "vs", "versus", "cómo", "paso a paso", "tips",
            "trucos", "mejor", "peor", "comparar", "análisis",
            
            # 🔥 MEJORA: Nuevas keywords para productos y contenido automatizable
            "productos", "recomendados", "precio", "barato", "características",
            "modelos", "accesorios", "snacks", "pienso", "comida", "alimentación",
            "oferta", "amazon", "comprar", "juguetes"
        ]

        keyword_lower = keyword.lower()
        return any(word in keyword_lower for word in automatizable_keywords)

    def get_monetization_potential(self, keyword):
        """
        Estimar potencial de monetización basado en categoría
        """
        keyword_lower = keyword.lower()

        for category, potential in self.monetization_categories.items():
            if category in keyword_lower:
                return potential

        return "Medio"  # Default

    def normalize_metrics(self, niches_data):
        """
        Normalizar métricas para comparación justa
        """
        if not niches_data:
            return niches_data

        # Extraer valores para normalización
        views_values = [niche['avg_views'] for niche in niches_data]
        likes_values = [niche['total_likes'] for niche in niches_data]
        comments_values = [niche['total_comments'] for niche in niches_data]

        # Calcular máximos para normalización
        max_views = max(views_values) if views_values else 1
        max_likes = max(likes_values) if likes_values else 1
        max_comments = max(comments_values) if comments_values else 1

        # Normalizar cada nicho
        for niche in niches_data:
            niche['views_norm'] = niche['avg_views'] / max_views
            niche['likes_norm'] = niche['total_likes'] / max_likes
            niche['comments_norm'] = niche['total_comments'] / max_comments
            niche['engagement_norm'] = (niche['likes_norm'] + niche['comments_norm']) / 2

        return niches_data

    def analyze_youtube_potential(self, keywords, max_keywords=10):
        """
        PASO 2: Validar keywords con YouTube Data API (con filtro de fecha)
        """
        validated_niches = []

        # Limitar número de keywords para no exceder cuota
        keywords_to_analyze = keywords[:max_keywords]

        for keyword in keywords_to_analyze:
            if self.daily_youtube_requests >= self.max_youtube_per_day:
                print("⚠️  Límite diario de YouTube API alcanzado")
                break

            try:
                print(f"📊 Analizando '{keyword}' en YouTube...")

                # Buscar videos CON FILTRO DE FECHA (últimos 12 meses)
                search_request = self.youtube.search().list(
                    q=keyword,
                    part="snippet",
                    type="video",
                    maxResults=15,  # Más videos para mejor análisis
                    order="relevance",
                    publishedAfter=self.date_limit  # 🔥 FILTRO DE FECHA MEJORA #3
                )
                search_response = search_request.execute()

                if not search_response['items']:
                    continue

                # Obtener estadísticas
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                stats_request = self.youtube.videos().list(
                    part="statistics",
                    id=",".join(video_ids)
                )
                stats_response = stats_request.execute()

                # Calcular métricas
                total_views = sum(int(item['statistics'].get('viewCount', 0))
                                for item in stats_response['items'])
                avg_views = total_views / len(stats_response['items']) if stats_response['items'] else 0

                # Calcular engagement adicional
                total_likes = sum(int(item['statistics'].get('likeCount', 0))
                                for item in stats_response['items'])
                total_comments = sum(int(item['statistics'].get('commentCount', 0))
                                   for item in stats_response['items'])

                # 🔥 MEJORAS #2 y #4: Automatización y Monetización
                niche_data = {
                    'keyword': keyword,
                    'video_count': len(search_response['items']),
                    'total_views': total_views,
                    'avg_views': avg_views,
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'competition_level': self._calculate_competition_level(avg_views),
                    'is_automatizable': self.is_automatizable(keyword),  # 🔥 MEJORA #2
                    'monetization_potential': self.get_monetization_potential(keyword),  # 🔥 MEJORA #4
                    'tipo_monetizacion': self.clasificar_monetizacion(keyword),  # 🔥 PUNTO 2: Nueva clasificación
                    'youtube_requests': 2  # search + stats
                }

                validated_niches.append(niche_data)
                self.daily_youtube_requests += 2

                time.sleep(random.uniform(1, 2))  # Pausa entre requests

            except HttpError as e:
                if e.resp.status == 403:
                    print("❌ Cuota de YouTube API excedida")
                    break
                else:
                    print(f"⚠️  Error con '{keyword}': {e}")
                    continue

        return validated_niches

    def _calculate_competition_level(self, avg_views):
        """
        Calcular nivel de competencia basado en views promedio
        """
        if avg_views < 1000:
            return "low"
        elif avg_views < 10000:
            return "medium"
        elif avg_views < 100000:
            return "high"
        else:
            return "very_high"

    def calculate_opportunity_score(self, niche_data):
        """
        PASO 3: Calcular Opportunity Score final con normalización
        """
        # 🔥 MEJORA #1: Usar métricas normalizadas para comparación justa
        views_score = niche_data.get('views_norm', 0.5)
        engagement_score = niche_data.get('engagement_norm', 0.5)

        # Competition score (inverso a la competencia)
        competition_scores = {"low": 1.0, "medium": 0.7, "high": 0.4, "very_high": 0.1}
        competition_score = competition_scores.get(niche_data['competition_level'], 0.5)

        # 🔥 MEJORA #2: Bonus por automatización
        automation_bonus = 0.2 if niche_data.get('is_automatizable', False) else 0.0

        # 🔥 MEJORA #4: Factor de monetización
        monetization_multipliers = {
            "Muy Alto": 1.2,
            "Alto": 1.0,
            "Medio": 0.8,
            "Bajo": 0.6
        }
        monetization_multiplier = monetization_multipliers.get(
            niche_data.get('monetization_potential', 'Medio'), 0.8
        )

        # Growth potential (estimado)
        growth_potential = random.uniform(0.4, 0.8)

        # 🔥 PUNTO 1: Pesos ajustados basados en razonamiento mejorado
        # - Views normalizadas: Más peso (35%) por ser indicador clave de demanda
        # - Competencia: Mantener importancia (25%) por facilidad de entrada
        # - Automatización: Más peso (20%) por escalabilidad
        # - Monetización: Más peso (15%) por rentabilidad directa
        # - Engagement: Reducir (5%) ya que está correlacionado con views
        
        final_score = (
            0.35 * views_score +           # 35% views (demanda del mercado)
            0.25 * competition_score +     # 25% competencia (facilidad entrada)
            0.20 * automation_bonus +      # 20% automatización (escalabilidad)
            0.15 * (monetization_multiplier - 0.8) +  # 15% monetización (rentabilidad)
            0.05 * engagement_score        # 5% engagement (correlacionado con views)
        )

        # Asegurar que el score esté entre 0 y 1
        final_score = max(0, min(1, final_score))

        return {
            'final_score': round(final_score, 3),
            'views_score': round(views_score, 3),
            'competition_score': round(competition_score, 3),
            'engagement_score': round(engagement_score, 3),
            'automation_bonus': round(automation_bonus, 3),
            'monetization_multiplier': round(monetization_multiplier, 3),
            'growth_potential': round(growth_potential, 3)
        }

    def run_single_analysis(self):
        """
        🔥 NUEVO: Ejecutar análisis de UNA SOLA keyword específica
        Reduce consumo de API a solo 2 requests por ejecución
        """
        print("🎯 ANÁLISIS INDIVIDUAL DE NICHO")
        print("=" * 50)

        # Pedir keyword al usuario
        while True:
            try:
                keyword = input("� Ingresa la keyword a analizar: ").strip()
                if keyword:
                    break
                else:
                    print("❌ La keyword no puede estar vacía. Intenta de nuevo.")
            except KeyboardInterrupt:
                print("\n⏹️  Análisis cancelado por el usuario")
                return []

        print(f"� Analizando keyword: '{keyword}'")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        # PASO 1: Analizar solo esta keyword en YouTube
        print("📺 Consultando YouTube Data API...")
        validated_niches = self.analyze_youtube_potential([keyword], max_keywords=1)

        if not validated_niches:
            print(f"❌ No se encontraron resultados para '{keyword}' en YouTube")
            return []

        niche = validated_niches[0]

        # 🔥 MEJORAS: Aplicar todas las funcionalidades mejoradas
        print("🔄 Aplicando mejoras del sistema...")

        # Normalizar métricas
        normalized_niches = self.normalize_metrics([niche])
        niche = normalized_niches[0]

        # Calcular scores finales
        scores = self.calculate_opportunity_score(niche)
        final_result = {**niche, **scores}

        print("✅ Análisis completado exitosamente!")
        return [final_result]

    def generate_report(self, results):
        """
        Generar reporte final con recomendaciones
        """
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL - TOP NICHOS RENTABLES")
        print("=" * 80)

        print(f"\n🎯 Analizados {len(results)} nichos potenciales")
        print(f"📊 API Requests usados: {self.daily_youtube_requests} (YouTube)")

        # Mostrar top 5 nichos
        print(f"\n🏆 TOP 5 NICHOS RECOMENDADOS:")
        print("-" * 80)

        for i, niche in enumerate(results[:5], 1):
            automatizable_icon = "🤖" if niche['is_automatizable'] else "👤"
            print(f"\n{i}. 🎯 {niche['keyword']}")
            print(f"   📊 Opportunity Score: {niche['final_score']:.3f}")
            print(f"   👥 Competencia: {niche['competition_level'].title()}")
            print(f"   📈 Views Promedio: {niche['avg_views']:,.0f}")
            print(f"   👍 Likes Totales: {niche['total_likes']:,}")
            print(f"   💬 Comentarios: {niche['total_comments']:,}")
            print(f"   🎬 Videos: {niche['video_count']}")
            print(f"   {automatizable_icon} Automatizable: {'Sí' if niche['is_automatizable'] else 'No'}")
            print(f"   💰 Monetización: {niche['monetization_potential']}")
            print(f"   📊 Views Normalizado: {niche.get('views_norm', 0):.3f}")
            print(f"   🎯 Engagement Normalizado: {niche.get('engagement_norm', 0):.3f}")

        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        print("-" * 80)

        if results:
            top_niche = results[0]
            print(f"🎯 Nicho Principal: '{top_niche['keyword']}' (Score: {top_niche['final_score']:.3f})")

            if top_niche['competition_level'] == 'low':
                print("✅ Baja competencia - ¡Excelente oportunidad para entrar!")
            elif top_niche['competition_level'] == 'medium':
                print("⚠️  Competencia media - Posible con diferenciación")
            else:
                print("🔴 Alta competencia - Considera sub-nichos específicos")

            # 🔥 MEJORAS: Recomendaciones de automatización y monetización
            if top_niche['is_automatizable']:
                print("🤖 Nicho automatizable - Perfecto para IA y producción masiva")
            else:
                print("👤 Nicho personalizado - Requiere contenido único y personal")

            if top_niche['monetization_potential'] in ['Muy Alto', 'Alto']:
                print("💰 Alto potencial monetario - Cursos, consultorías, productos premium")
            elif top_niche['monetization_potential'] == 'Medio':
                print("📈 Potencial moderado - Afiliados y productos digitales")
            else:
                print("⚠️  Potencial bajo - Enfócate en engagement y crecimiento")

            # Recomendaciones específicas por views
            if top_niche['avg_views'] > 50000:
                print("� Contenido premium viable - Alta producción de valor")
            elif top_niche['avg_views'] > 10000:
                print("📊 Contenido educativo - Tutoriales y guías especializadas")

        print(f"\n⏰ Análisis completado: {datetime.now().strftime('%H:%M:%S')}")

    def export_results(self, results, filename=None):
        """
        🔥 MEJORA #5: Exportar resultados a CSV y Markdown
        """
        if not results:
            print("❌ No hay resultados para exportar")
            return

        # Generar nombre de archivo con timestamp
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"nichos_analisis_{timestamp}"

        # Exportar a CSV
        csv_filename = f"{filename}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'keyword', 'final_score', 'competition_level', 'avg_views',
                'total_likes', 'total_comments', 'video_count', 'is_automatizable',
                'monetization_potential', 'tipo_monetizacion', 'views_norm', 'engagement_norm'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'keyword': result['keyword'],
                    'final_score': result['final_score'],
                    'competition_level': result['competition_level'],
                    'avg_views': result['avg_views'],
                    'total_likes': result['total_likes'],
                    'total_comments': result['total_comments'],
                    'video_count': result['video_count'],
                    'is_automatizable': result['is_automatizable'],
                    'monetization_potential': result['monetization_potential'],
                    'tipo_monetizacion': result.get('tipo_monetizacion', 'No definido'),  # 🔥 PUNTO 2
                    'views_norm': result.get('views_norm', 0),
                    'engagement_norm': result.get('engagement_norm', 0)
                })

        # Exportar a Markdown
        md_filename = f"{filename}.md"
        with open(md_filename, 'w', encoding='utf-8') as mdfile:
            mdfile.write("# 📊 Análisis de Nichos Rentables\n\n")
            mdfile.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            mdfile.write(f"**Nichos analizados:** {len(results)}\n\n")

            mdfile.write("## 🏆 Top Nichos Recomendados\n\n")
            mdfile.write("| Nicho | Score | Competencia | Views | Automatizable | Monetización | Tipo |\n")
            mdfile.write("|-------|-------|-------------|-------|---------------|--------------|------|\n")

            for result in results[:10]:  # Top 10
                automatizable_icon = "✅" if result['is_automatizable'] else "❌"
                tipo_monetizacion = result.get('tipo_monetizacion', 'No definido')
                mdfile.write(f"| {result['keyword']} | {result['final_score']} | {result['competition_level'].title()} | {result['avg_views']:,.0f} | {automatizable_icon} | {result['monetization_potential']} | {tipo_monetizacion} |\n")

            mdfile.write("\n## 📈 Estadísticas Generales\n\n")
            mdfile.write(f"- **Views promedio:** {sum(r['avg_views'] for r in results)/len(results):,.0f}\n")
            mdfile.write(f"- **Nichos automatizables:** {sum(1 for r in results if r['is_automatizable'])}/{len(results)}\n")
            mdfile.write(f"- **Monetización alta:** {sum(1 for r in results if r['monetization_potential'] in ['Muy Alto', 'Alto'])}/{len(results)}\n")
            
            # 🔥 PUNTO 2: Estadísticas de tipos de monetización
            mdfile.write(f"- **Afiliación + Anuncios:** {sum(1 for r in results if r.get('tipo_monetizacion') == 'Afiliación + Anuncios')}/{len(results)}\n")
            mdfile.write(f"- **Solo Afiliación:** {sum(1 for r in results if r.get('tipo_monetizacion') == 'Solo Afiliación')}/{len(results)}\n")
            mdfile.write(f"- **Solo Anuncios:** {sum(1 for r in results if r.get('tipo_monetizacion') == 'Solo Anuncios')}/{len(results)}\n")

        print(f"✅ Resultados exportados:")
        print(f"   📄 CSV: {csv_filename}")
        print(f"   📋 Markdown: {md_filename}")


def main():
    """
    Función principal del sistema mejorado con opciones flexibles
    """
    print("🎯 SISTEMA MEJORADO DE ANÁLISIS DE NICHOS")
    print("📊 Con normalización, automatización y monetización")
    print("=" * 60)

    print("� OPCIONES DISPONIBLES:")
    print("1. 🔍 Análisis Individual (1 keyword) - 2 API requests")
    print("2. 📊 Análisis Completo (12 keywords) - 24 API requests")
    print("=" * 60)

    # Inicializar analizador mejorado
    analyzer = NicheAnalyzerEnhanced()

    try:
        # Menú de opciones
        while True:
            try:
                choice = input("👆 Elige opción (1 o 2): ").strip()
                if choice in ['1', '2']:
                    break
                else:
                    print("❌ Opción inválida. Ingresa 1 o 2.")
            except KeyboardInterrupt:
                print("\n⏹️  Programa cancelado por el usuario")
                return

        # Ejecutar análisis según la opción elegida
        if choice == '1':
            print("\n🎯 MODO: ANÁLISIS INDIVIDUAL")
            print("💡 Solo consume 2 requests de API - Perfecto para testing")
            results = analyzer.run_single_analysis()
        else:
            print("\n📊 MODO: ANÁLISIS COMPLETO")
            print("💡 Consume 24 requests de API - Análisis exhaustivo")
            results = analyzer.run_basic_analysis()

        if results:
            # Generar reporte
            analyzer.generate_report(results)

            # 🔥 MEJORA #5: Exportar resultados
            analyzer.export_results(results)

            print(f"\n✅ Análisis completado exitosamente")
            print(f"📊 Procesados {len(results)} nichos potenciales")
            print(f"📁 Archivos exportados en el directorio actual")
        else:
            print("\n❌ No se pudieron obtener resultados")

    except KeyboardInterrupt:
        print("\n⏹️  Análisis interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el análisis: {e}")


if __name__ == "__main__":
    main()
