"""
Sistema Automatizado de Análisis de Nichos Rentables
Flujo Optimizado: Google Trends → Filtrado → YouTube Validation → Scoring

Autor: Proyecto 201 digital
Fecha: 28/08/2025
Versión: 1.0 - Opción A (Sistema automático con límites diarios)
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Añadir la carpeta credentials al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
from config import YOUTUBE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_COUNTRY


class NicheAnalyzer:
    """
    Sistema automatizado para encontrar nichos rentables en YouTube
    """

    def __init__(self):
        """Inicializar el analizador con configuraciones optimizadas"""
        self.pytrends = TrendReq(hl=DEFAULT_LANGUAGE, tz=360)
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Configuración para límites de API (Opción A)
        self.daily_youtube_quota = 10000  # Unidades por día
        self.daily_trends_requests = 0
        self.daily_youtube_requests = 0
        self.max_trends_per_day = 50  # Límite conservador para Trends
        self.max_youtube_per_day = 100  # Límite conservador para YouTube

        # Pesos para scoring
        self.weights = {
            'trends_score': 0.3,
            'competition_score': 0.25,
            'monetization_potential': 0.25,
            'growth_potential': 0.2
        }

    def get_trending_topics(self, category="all", geo=DEFAULT_COUNTRY):
        """
        PASO 1: Obtener tendencias actuales de Google Trends
        """
        if self.daily_trends_requests >= self.max_trends_per_day:
            print("⚠️  Límite diario de Trends alcanzado")
            return []

        try:
            print("🔥 Obteniendo tendencias de Google Trends...")

            # Obtener tendencias diarias
            self.pytrends.build_payload(kw_list=[""], geo=geo, timeframe="now 1-d")
            trending_searches = self.pytrends.trending_searches(pn=f"{DEFAULT_LANGUAGE.lower()}-{geo.lower()}")

            self.daily_trends_requests += 1

            # Extraer keywords principales
            keywords = []
            if not trending_searches.empty:
                keywords = trending_searches.head(20)['title'].tolist()

            print(f"📈 Encontradas {len(keywords)} tendencias actuales")
            return keywords

        except Exception as e:
            print(f"❌ Error obteniendo tendencias: {e}")
            return []

    def get_related_keywords(self, seed_keywords, max_related=5):
        """
        PASO 2: Obtener keywords relacionadas con alto potencial
        """
        related_keywords = []

        for keyword in seed_keywords[:3]:  # Limitar para no exceder cuota
            if self.daily_trends_requests >= self.max_trends_per_day:
                break

            try:
                print(f"🔍 Buscando keywords relacionadas para: {keyword}")

                # Obtener sugerencias relacionadas
                self.pytrends.build_payload(kw_list=[keyword], timeframe="now 7-d")
                suggestions = self.pytrends.suggestions(keyword=keyword)

                if suggestions:
                    # Filtrar por relevancia
                    filtered = [s['title'] for s in suggestions[:max_related]]
                    related_keywords.extend(filtered)

                self.daily_trends_requests += 1
                time.sleep(random.uniform(1, 3))  # Pausa para evitar bloqueo

            except Exception as e:
                print(f"⚠️  Error con keyword '{keyword}': {e}")
                continue

        # Remover duplicados y limitar
        unique_keywords = list(set(related_keywords))[:15]
        print(f"🎯 Encontradas {len(unique_keywords)} keywords relacionadas")
        return unique_keywords

    def analyze_youtube_potential(self, keywords):
        """
        PASO 3: Validar keywords con YouTube Data API
        """
        validated_niches = []

        for keyword in keywords:
            if self.daily_youtube_requests >= self.max_youtube_per_day:
                print("⚠️  Límite diario de YouTube API alcanzado")
                break

            try:
                print(f"📊 Analizando '{keyword}' en YouTube...")

                # Buscar videos
                search_request = self.youtube.search().list(
                    q=keyword,
                    part="snippet",
                    type="video",
                    maxResults=10,
                    order="relevance"
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

                niche_data = {
                    'keyword': keyword,
                    'video_count': len(search_response['items']),
                    'total_views': total_views,
                    'avg_views': avg_views,
                    'competition_level': self._calculate_competition_level(avg_views),
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
        PASO 4: Calcular Opportunity Score final
        """
        trends_score = random.uniform(0.1, 1.0)  # Simulado - en producción usar datos reales

        # Competition score (inverso a la competencia)
        competition_scores = {"low": 1.0, "medium": 0.7, "high": 0.4, "very_high": 0.1}
        competition_score = competition_scores.get(niche_data['competition_level'], 0.5)

        # Monetization potential basado en views
        if niche_data['avg_views'] > 50000:
            monetization_potential = 0.9
        elif niche_data['avg_views'] > 10000:
            monetization_potential = 0.7
        elif niche_data['avg_views'] > 1000:
            monetization_potential = 0.5
        else:
            monetization_potential = 0.2

        # Growth potential (estimado)
        growth_potential = random.uniform(0.3, 0.9)

        # Calcular score final
        final_score = (
            self.weights['trends_score'] * trends_score +
            self.weights['competition_score'] * competition_score +
            self.weights['monetization_potential'] * monetization_potential +
            self.weights['growth_potential'] * growth_potential
        )

        return {
            'final_score': round(final_score, 3),
            'trends_score': round(trends_score, 3),
            'competition_score': round(competition_score, 3),
            'monetization_potential': round(monetization_potential, 3),
            'growth_potential': round(growth_potential, 3)
        }

    def run_daily_analysis(self):
        """
        Ejecutar análisis diario completo
        """
        print("🚀 Iniciando análisis diario de nichos rentables...")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # PASO 1: Obtener tendencias
        trending_topics = self.get_trending_topics()
        if not trending_topics:
            print("❌ No se pudieron obtener tendencias")
            return []

        # PASO 2: Obtener keywords relacionadas
        related_keywords = self.get_related_keywords(trending_topics)
        if not related_keywords:
            print("❌ No se encontraron keywords relacionadas")
            return []

        # PASO 3: Validar con YouTube
        validated_niches = self.analyze_youtube_potential(related_keywords)
        if not validated_niches:
            print("❌ No se pudieron validar nichos en YouTube")
            return []

        # PASO 4: Calcular scores finales
        final_results = []
        for niche in validated_niches:
            scores = self.calculate_opportunity_score(niche)
            niche_result = {**niche, **scores}
            final_results.append(niche_result)

        # Ordenar por opportunity score
        final_results.sort(key=lambda x: x['final_score'], reverse=True)

        return final_results

    def generate_report(self, results):
        """
        Generar reporte final con recomendaciones
        """
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL - TOP NICHOS RENTABLES")
        print("=" * 80)

        print(f"\n🎯 Analizados {len(results)} nichos potenciales")
        print(f"📈 API Requests - Trends: {self.daily_trends_requests}, YouTube: {self.daily_youtube_requests}")

        # Mostrar top 5 nichos
        print(f"\n🏆 TOP 5 NICHOS RECOMENDADOS:")
        print("-" * 80)

        for i, niche in enumerate(results[:5], 1):
            print(f"\n{i}. 🎯 {niche['keyword']}")
            print(f"   📊 Opportunity Score: {niche['final_score']:.3f}")
            print(f"   👥 Competencia: {niche['competition_level'].title()}")
            print(f"   📈 Views Promedio: {niche['avg_views']:,.0f}")
            print(f"   🎬 Videos: {niche['video_count']}")
            print(f"   💰 Potencial Monetización: {niche['monetization_potential']:.1f}/1.0")

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

        print(f"\n⏰ Próximo análisis: {datetime.now() + timedelta(days=1)}")


def main():
    """
    Función principal del sistema automatizado
    """
    print("🎯 SISTEMA AUTOMATIZADO DE ANÁLISIS DE NICHOS")
    print("📊 Opción A: Sistema automático con límites diarios")
    print("🔄 Flujo: Google Trends → Filtrado → YouTube → Scoring")
    print("=" * 60)

    # Inicializar analizador
    analyzer = NicheAnalyzer()

    try:
        # Ejecutar análisis diario
        results = analyzer.run_daily_analysis()

        if results:
            # Generar reporte
            analyzer.generate_report(results)

            print(f"\n✅ Análisis completado exitosamente")
            print(f"📊 Procesados {len(results)} nichos potenciales")
        else:
            print("\n❌ No se pudieron obtener resultados")

    except KeyboardInterrupt:
        print("\n⏹️  Análisis interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el análisis: {e}")


if __name__ == "__main__":
    main()
