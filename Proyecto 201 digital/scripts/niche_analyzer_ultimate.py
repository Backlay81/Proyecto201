"""
Sistema Automatizado de Análisis de Nichos Rentables - VERSIÓN COMPLETA
Google Trends + YouTube + Todas las Mejoras Implementadas + Tracking en Tiempo Real
Proyecto 201 digital - Versión Ultimate
Fecha: 29/08/2025
"""

import sys
import os
import time
import random
import csv
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Añadir la carpeta credentials al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
from config import YOUTUBE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_COUNTRY

# Importar el sistema de tracking
from api_usage_tracker import tracker, track_youtube_search, track_youtube_videos, track_trends_query


class NicheAnalyzerUltimate:
    """
    Sistema ULTIMATE para encontrar nichos rentables
    Combina Google Trends + YouTube + Todas las mejoras
    """

    def __init__(self):
        """Inicializar el analizador completo"""
        try:
            self.pytrends = TrendReq(hl=DEFAULT_LANGUAGE, tz=360)
            self.trends_available = True
            print("✅ Google Trends inicializado correctamente")
        except Exception as e:
            self.trends_available = False
            print(f"⚠️  Google Trends no disponible: {e}")
            
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Configuración para límites de API - MODO TESTING
        self.daily_youtube_requests = 0
        self.daily_trends_requests = 0
        self.max_youtube_per_day = 20   # 🔥 REDUCIDO: Antes 100, ahora 20
        self.max_trends_per_day = 10    # 🔥 REDUCIDO: Antes 50, ahora 10

        # 🔥 MODO TESTING: Solo 3 keywords para probar funcionalidad
        self.testing_mode = True
        self.max_keywords_testing = 3   # Solo 3 keywords = 6 requests YouTube
        # MODO ULTRA_TESTING: minimizar consumo al máximo para pulir el script
        self.ultra_testing = False
        # cuando ultra_testing=True: maxResults=1 y hacemos batching de videos.list (1 request por análisis)
        self.ultra_max_results = 1

        # Fecha límite para contenido reciente (últimos 12 meses)
        self.date_limit = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Keywords predefinidos para fallback - MODO TESTING
        self.fallback_keywords = [
            # 🔥 SOLO 3 KEYWORDS PARA TESTING (6 requests YouTube total)
            "finanzas personales",
            "mejores productos tecnológicos",  # Debería ser Afiliación + Anuncios
            "review criptomonedas"            # Debería ser Afiliación + Anuncios
        ]

    def get_trending_keywords(self):
        """
        🔥 FUNCIÓN 1: Obtener keywords trending - MODO TESTING OPTIMIZADO
        """
        trending_keywords = []
        
        if not self.trends_available:
            print("📝 Google Trends no disponible - usando keywords predefinidas (MODO TESTING)")
            return self.fallback_keywords  # Solo 3 keywords
            
        try:
            print("📈 Obteniendo tendencias actuales de Google Trends... (MODO TESTING)")
            
            # 🔥 TESTING: Solo 1 trending search para minimizar requests
            if self.daily_trends_requests < self.max_trends_per_day:
                # 🔥 TRACKING: Registrar request de Trends
                track_trends_query("trending_searches_spain")
                
                trending_searches = self.pytrends.trending_searches(pn='spain')
                trending_keywords.extend(trending_searches[0].head(2).tolist())  # Solo 2
                self.daily_trends_requests += 1
                print(f"   ✅ {len(trending_keywords)} tendencias obtenidas")
                
            # 🔥 TESTING: Solo 1 related query para minimizar requests
            if self.daily_trends_requests < self.max_trends_per_day and len(trending_keywords) < 3:
                try:
                    # 🔥 TRACKING: Registrar request de Trends
                    track_trends_query("related_queries_finanzas")
                    
                    self.pytrends.build_payload(['finanzas'], timeframe='now 1-m')
                    related = self.pytrends.related_queries()
                    
                    if 'finanzas' in related and related['finanzas']['rising'] is not None:
                        rising_queries = related['finanzas']['rising']['query'].head(1).tolist()  # Solo 1
                        trending_keywords.extend(rising_queries)
                        print(f"   ✅ Keywords relacionadas: {len(rising_queries)}")
                    
                    self.daily_trends_requests += 1
                    
                except Exception as e:
                    print(f"   ⚠️  Error con related queries: {str(e)[:30]}...")
                    
        except Exception as e:
            print(f"❌ Error en Google Trends: {e}")
            print("📝 Usando keywords predefinidas como fallback (MODO TESTING)")
            return self.fallback_keywords
            
        # Si no hay suficientes, usar fallback
        if len(trending_keywords) < 3:
            trending_keywords.extend(self.fallback_keywords)
            
        # 🔥 TESTING: Máximo 3 keywords para minimizar consumo
        return trending_keywords[:3]

    def clasificar_monetizacion(self, keyword):
        """
        🔥 MEJORA: Clasificación avanzada del tipo de monetización
        """
        keyword_lower = keyword.lower()
        
        # 🔗 Palabras clave para AFILIACIÓN
        afiliacion = [
            "comprar", "mejores", "review", "productos", "comparativa", "guía",
            "precio", "barato", "amazon", "oferta", "ranking", "pienso", 
            "juguetes", "accesorios", "snacks", "alimentación", "recomendación", 
            "top", "análisis", "prueba", "características", "modelos"
        ]
        
        # 💰 Palabras clave para ANUNCIOS (CPM alto)
        anuncios = [
            "finanzas", "financiero", "financiera", "financieros", "invertir", 
            "inversión", "trading", "seguros", "banca", "abogado", "consultoría", 
            "marketing", "coaching", "educación", "psicología", "cuenta", "cuentas", 
            "remunerada", "remuneradas", "interés", "ahorros", "cuenta bancaria", 
            "cuenta sin comisiones", "forex", "bolsa", "préstamos", "tarjetas", 
            "banco", "cripto", "criptomonedas", "emprendimiento"
        ]
        
        tiene_afiliacion = any(word in keyword_lower for word in afiliacion)
        tiene_anuncios = any(word in keyword_lower for word in anuncios)
        
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
        """
        automatizable_keywords = [
            # Keywords estructuradas
            "review", "top", "mejores", "comparativa", "tutorial", "guía",
            "ranking", "vs", "versus", "cómo", "paso a paso", "tips",
            "trucos", "mejor", "peor", "comparar", "análisis",
            # Keywords de productos
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
        
        monetization_categories = {
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

        for category, potential in monetization_categories.items():
            if category in keyword_lower:
                return potential

        return "Medio"

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

    def analyze_youtube_potential(self, keywords, max_keywords=3):  # 🔥 REDUCIDO: Antes 10, ahora 3
        """
        Validar keywords con YouTube Data API - MODO TESTING OPTIMIZADO
        """
        validated_niches = []
        keywords_to_analyze = keywords[:max_keywords]  # Máximo 3 keywords

        for keyword in keywords_to_analyze:
            if self.daily_youtube_requests >= self.max_youtube_per_day:
                print("⚠️  Límite diario de YouTube API alcanzado")
                break

            try:
                print(f"📊 Analizando '{keyword}' en YouTube... (Testing)")

                # 🔥 TRACKING: Registrar request de búsqueda
                track_youtube_search(keyword)

                # 🔥 MODO ULTRA_TESTING: reducir maxResults a 1 para gastar el mínimo
                max_results = self.ultra_max_results if self.ultra_testing else 10
                search_request = self.youtube.search().list(
                    q=keyword,
                    part="snippet",
                    type="video",
                    maxResults=max_results,
                    order="relevance",
                    publishedAfter=self.date_limit
                )
                search_response = search_request.execute()

                if not search_response['items']:
                    continue

                # Obtener estadísticas
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                # 🔥 Modo Ultra: batchear videos.list para 1 request por análisis
                # Registrar videos.list como 1 request
                track_youtube_videos(keyword, len(video_ids))
                
                # En ultra_testing hacemos una única llamada con todos los ids (ya es así)
                stats_request = self.youtube.videos().list(
                    part="statistics",
                    id=",".join(video_ids)
                )
                stats_response = stats_request.execute()

                # Calcular métricas
                total_views = sum(int(item['statistics'].get('viewCount', 0))
                                for item in stats_response['items'])
                avg_views = total_views / len(stats_response['items']) if stats_response['items'] else 0

                total_likes = sum(int(item['statistics'].get('likeCount', 0))
                                for item in stats_response['items'])
                total_comments = sum(int(item['statistics'].get('commentCount', 0))
                                   for item in stats_response['items'])

                # Aplicar todas las mejoras
                niche_data = {
                    'keyword': keyword,
                    'video_count': len(search_response['items']),
                    'total_views': total_views,
                    'avg_views': avg_views,
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'competition_level': self._calculate_competition_level(avg_views),
                    'is_automatizable': self.is_automatizable(keyword),
                    'monetization_potential': self.get_monetization_potential(keyword),
                    'tipo_monetizacion': self.clasificar_monetizacion(keyword),
                    'youtube_requests': 2
                }

                validated_niches.append(niche_data)
                self.daily_youtube_requests += 2
                time.sleep(random.uniform(1, 2))

            except HttpError as e:
                if e.resp.status == 403:
                    print("❌ Cuota de YouTube API excedida")
                    break
                else:
                    print(f"⚠️  Error con '{keyword}': {e}")
                    continue

        return validated_niches

    def _calculate_competition_level(self, avg_views):
        """Calcular nivel de competencia basado en views promedio"""
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
        Calcular Opportunity Score final con normalización
        """
        views_score = niche_data.get('views_norm', 0.5)
        engagement_score = niche_data.get('engagement_norm', 0.5)

        competition_scores = {"low": 1.0, "medium": 0.7, "high": 0.4, "very_high": 0.1}
        competition_score = competition_scores.get(niche_data['competition_level'], 0.5)

        automation_bonus = 0.2 if niche_data.get('is_automatizable', False) else 0.0

        monetization_multipliers = {
            "Muy Alto": 1.2, "Alto": 1.0, "Medio": 0.8, "Bajo": 0.6
        }
        monetization_multiplier = monetization_multipliers.get(
            niche_data.get('monetization_potential', 'Medio'), 0.8
        )

        # Pesos optimizados
        final_score = (
            0.35 * views_score +           # 35% views (demanda del mercado)
            0.25 * competition_score +     # 25% competencia (facilidad entrada)
            0.20 * automation_bonus +      # 20% automatización (escalabilidad)
            0.15 * (monetization_multiplier - 0.8) +  # 15% monetización
            0.05 * engagement_score        # 5% engagement
        )

        final_score = max(0, min(1, final_score))

        return {
            'final_score': round(final_score, 3),
            'views_score': round(views_score, 3),
            'competition_score': round(competition_score, 3),
            'engagement_score': round(engagement_score, 3),
            'automation_bonus': round(automation_bonus, 3),
            'monetization_multiplier': round(monetization_multiplier, 3)
        }

    def run_complete_analysis(self):
        """
        🔥 ANÁLISIS COMPLETO MODO TESTING: Solo 3 keywords = 6 requests YouTube máximo
        """
        print("🧪 INICIANDO ANÁLISIS COMPLETO - MODO TESTING")
        print("💡 Máximo 3 keywords = 6 requests YouTube (ahorro de cuota)")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # PASO 1: Obtener keywords (3 máximo)
        trending_keywords = self.get_trending_keywords()
        print(f"🎯 Keywords para testing: {len(trending_keywords)}")
        for i, kw in enumerate(trending_keywords, 1):
            print(f"   {i}. {kw}")

        # PASO 2: Validar con YouTube (máximo 3 keywords = 6 requests)
        print(f"\n📺 Validando en YouTube (máximo {len(trending_keywords) * 2} requests)...")
        validated_niches = self.analyze_youtube_potential(trending_keywords, max_keywords=3)

        if not validated_niches:
            print("❌ No se pudieron validar nichos")
            return []

        # PASO 3: Normalizar métricas
        print("🔄 Normalizando métricas...")
        validated_niches = self.normalize_metrics(validated_niches)

        # PASO 4: Calcular scores finales
        final_results = []
        for niche in validated_niches:
            scores = self.calculate_opportunity_score(niche)
            niche_result = {**niche, **scores}
            final_results.append(niche_result)

        # Ordenar por opportunity score
        final_results.sort(key=lambda x: x['final_score'], reverse=True)

        return final_results

    def run_single_keyword(self, keyword, fetch_video_stats=True, max_results=None):
        """Ejecutar análisis para UNA sola keyword (ahorro máximo)."""
        print(f"🧪 INICIANDO ANÁLISIS - KEYWORD: '{keyword}'")
        # Controlar parámetros
        if max_results is None:
            max_results = 10 if not self.ultra_testing else self.ultra_max_results

        # Obtener solo la keyword solicitada
        validated = self.analyze_youtube_potential([keyword], max_keywords=1)
        if not validated:
            print("❌ No se obtuvieron datos para la keyword")
            return []

        # Normalizar y calcular scores
        validated = self.normalize_metrics(validated)
        final = []
        for niche in validated:
            scores = self.calculate_opportunity_score(niche)
            final.append({**niche, **scores})

        # Mostrar y devolver
        self.generate_report(final)
        return final

    def generate_report(self, results):
        """Generar reporte final"""
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL - ANÁLISIS COMPLETO CON GOOGLE TRENDS")
        print("=" * 80)

        print(f"\n🎯 Analizados {len(results)} nichos potenciales")
        print(f"📊 API Requests - Trends: {self.daily_trends_requests}, YouTube: {self.daily_youtube_requests}")

        # 🔥 NUEVO: Mostrar estado actual del tracker
        print("\n" + "=" * 50)
        tracker.show_status()
        print("=" * 50)

        print(f"\n🏆 TOP 5 NICHOS RECOMENDADOS:")
        print("-" * 80)

        for i, niche in enumerate(results[:5], 1):
            automatizable_icon = "🤖" if niche['is_automatizable'] else "👤"
            print(f"\n{i}. 🎯 {niche['keyword']}")
            print(f"   📊 Opportunity Score: {niche['final_score']:.3f}")
            print(f"   👥 Competencia: {niche['competition_level'].title()}")
            print(f"   📈 Views Promedio: {niche['avg_views']:,.0f}")
            print(f"   {automatizable_icon} Automatizable: {'Sí' if niche['is_automatizable'] else 'No'}")
            print(f"   💰 Monetización: {niche['monetization_potential']}")
            print(f"   🎯 Tipo: {niche['tipo_monetizacion']}")

        print(f"\n⏰ Análisis completado: {datetime.now().strftime('%H:%M:%S')}")

    def export_results(self, results, filename=None):
        """Exportar resultados a CSV y Markdown"""
        if not results:
            print("❌ No hay resultados para exportar")
            return

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"nichos_trends_analisis_{timestamp}"

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
                    'tipo_monetizacion': result.get('tipo_monetizacion', 'No definido'),
                    'views_norm': result.get('views_norm', 0),
                    'engagement_norm': result.get('engagement_norm', 0)
                })

        # Exportar a Markdown
        md_filename = f"{filename}.md"
        with open(md_filename, 'w', encoding='utf-8') as mdfile:
            mdfile.write("# 📊 Análisis de Nichos Rentables - CON GOOGLE TRENDS\n\n")
            mdfile.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            mdfile.write(f"**Nichos analizados:** {len(results)}\n\n")
            mdfile.write(f"**Fuente:** Google Trends + YouTube Data API\n\n")

            mdfile.write("## 🏆 Top Nichos Recomendados\n\n")
            mdfile.write("| Nicho | Score | Competencia | Views | Automatizable | Monetización | Tipo |\n")
            mdfile.write("|-------|-------|-------------|-------|---------------|--------------|------|\n")

            for result in results[:10]:
                automatizable_icon = "✅" if result['is_automatizable'] else "❌"
                tipo_monetizacion = result.get('tipo_monetizacion', 'No definido')
                mdfile.write(f"| {result['keyword']} | {result['final_score']} | {result['competition_level'].title()} | {result['avg_views']:,.0f} | {automatizable_icon} | {result['monetization_potential']} | {tipo_monetizacion} |\n")

            mdfile.write("\n## 📈 Estadísticas Generales\n\n")
            mdfile.write(f"- **Views promedio:** {sum(r['avg_views'] for r in results)/len(results):,.0f}\n")
            mdfile.write(f"- **Nichos automatizables:** {sum(1 for r in results if r['is_automatizable'])}/{len(results)}\n")
            mdfile.write(f"- **Monetización alta:** {sum(1 for r in results if r['monetization_potential'] in ['Muy Alto', 'Alto'])}/{len(results)}\n")
            mdfile.write(f"- **Afiliación + Anuncios:** {sum(1 for r in results if r.get('tipo_monetizacion') == 'Afiliación + Anuncios')}/{len(results)}\n")

        print(f"✅ Resultados exportados:")
        print(f"   📄 CSV: {csv_filename}")
        print(f"   📋 Markdown: {md_filename}")


def main():
    """
    Función principal del sistema ULTIMATE
    """
    print("🔥 SISTEMA ULTIMATE DE ANÁLISIS DE NICHOS")
    print("📈 Google Trends + YouTube + Todas las Mejoras")
    print("=" * 60)

    analyzer = NicheAnalyzerUltimate()

    try:
        # Ejecutar análisis completo
        results = analyzer.run_complete_analysis()

        if results:
            # Generar reporte
            analyzer.generate_report(results)

            # Exportar resultados
            analyzer.export_results(results)

            print(f"\n✅ Análisis ULTIMATE completado exitosamente")
            print(f"📊 Procesados {len(results)} nichos trending")
            print(f"📁 Archivos exportados con prefijo 'nichos_trends_'")
        else:
            print("\n❌ No se pudieron obtener resultados")

    except KeyboardInterrupt:
        print("\n⏹️  Análisis interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el análisis: {e}")


if __name__ == "__main__":
    main()
