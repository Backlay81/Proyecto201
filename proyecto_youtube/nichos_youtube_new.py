"""
Analizador de Nichos YouTube - Versión Mejorada
===============================================
Sistema para analizar nichos rentables en YouTube con:
- Análisis avanzado de automatización (títulos, descripciones, tags)
- Clasificación de canales por tamaño (pequeños/medianos/grandes)
- Detección de señales de automatización ES/EN
- Exportación completa CSV/MD con métricas ampliadas
"""

import sys
import os
import time
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

# Añadir utils al path para importar módulos locales
sys.path.append(str(Path(__file__).resolve().parent / 'utils'))

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import argparse

# Importar configuración local
sys.path.append(str(Path(__file__).resolve().parent / 'credentials'))
from config import YOUTUBE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_COUNTRY

# Importar sistema de tracking
from api_usage_tracker import tracker, track_youtube_search, track_youtube_videos


class NicheAnalyzerYouTube:
    """
    Analizador de nichos YouTube con análisis avanzado de automatización y canales
    """

    def __init__(self):
        """Inicializar el analizador"""
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Configuración de límites
        self.daily_youtube_requests = 0
        self.max_youtube_per_day = 50
        
        # Fecha límite para contenido reciente (últimos 12 meses)
        self.date_limit = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')

    def analyze_automatizable_advanced(self, video_data_list, geo_region='ES'):
        """
        Análisis avanzado de automatización basado en títulos, descripciones y tags
        """
        # Diccionarios de señales ES/EN
        signals_es = set([
            "tutorial", "plantilla", "guion", "script", "herramienta", "automatización",
            "paso a paso", "explicado fácil", "ejemplo", "review", "top", "mejores",
            "comparativa", "guía", "ranking", "vs", "versus", "cómo", "tips", "trucos",
            "mejor", "peor", "comparar", "análisis", "productos", "recomendados",
            "precio", "barato", "características", "modelos", "accesorios"
        ])

        signals_en = set([
            "tutorial", "template", "script", "tool", "automation", "ai",
            "step by step", "explained", "example", "review", "top", "best",
            "comparison", "guide", "ranking", "vs", "versus", "how to", "tips",
            "tricks", "better", "worse", "compare", "analysis", "products",
            "recommended", "price", "cheap", "features", "models", "accessories"
        ])

        # Seleccionar diccionario según región
        signals_lookup = signals_es if geo_region == 'ES' else signals_en

        total_videos_analyzed = min(len(video_data_list), 5)
        if total_videos_analyzed == 0:
            return {
                'automatizable_status': 'NO',
                'automatizable_ratio': 0.0,
                'videos_with_signals': 0,
                'automatizable_signals': []
            }

        videos_with_signals = 0
        detected_signals = set()

        for video_data in video_data_list[:5]:
            snippet = video_data.get('snippet', {})
            title = (snippet.get('title') or '').lower()
            description = (snippet.get('description') or '').lower()
            tags = [t.lower() for t in (snippet.get('tags') or [])]

            text_corpus = ' '.join([title, description, ' '.join(tags)])

            found_in_video = False
            for signal in signals_lookup:
                if signal in text_corpus:
                    detected_signals.add(signal)
                    found_in_video = True

            if found_in_video:
                videos_with_signals += 1

        # Calcular ratio y clasificar
        automatizable_ratio = round((videos_with_signals / total_videos_analyzed * 100), 1)

        if videos_with_signals >= 2:
            automatizable_status = 'YES'
        elif videos_with_signals == 1:
            automatizable_status = 'PARTIAL'
        else:
            automatizable_status = 'NO'

        return {
            'automatizable_status': automatizable_status,
            'automatizable_ratio': automatizable_ratio,
            'videos_with_signals': videos_with_signals,
            'automatizable_signals': sorted(detected_signals)
        }

    def analyze_channel_sizes(self, video_data_list):
        """
        Analizar tamaño de canales por suscriptores
        """
        channel_ids = []
        for video_data in video_data_list[:5]:
            snippet = video_data.get('snippet', {})
            channel_id = snippet.get('channelId')
            if channel_id:
                channel_ids.append(channel_id)

        if not channel_ids:
            return {
                'small_channels_ratio': 0.0,
                'medium_channels_ratio': 0.0,
                'large_channels_ratio': 0.0,
                'unknown_channels_ratio': 100.0
            }

        # Obtener información de canales
        small_count = 0
        medium_count = 0
        large_count = 0
        unknown_count = 0

        try:
            # Solicitar información de canales en lotes
            channels_request = self.youtube.channels().list(
                part="statistics",
                id=",".join(channel_ids)
            )
            channels_response = channels_request.execute()

            for channel in channels_response.get('items', []):
                subscriber_count = int(channel.get('statistics', {}).get('subscriberCount', 0))
                
                if subscriber_count < 50000:
                    small_count += 1
                elif 50000 <= subscriber_count <= 500000:
                    medium_count += 1
                else:
                    large_count += 1

            # Contar canales sin datos
            analyzed_channels = len(channels_response.get('items', []))
            unknown_count = len(channel_ids) - analyzed_channels

        except Exception as e:
            print(f"   ⚠️  Error obteniendo datos de canales: {e}")
            unknown_count = len(channel_ids)

        total_channels = len(channel_ids)
        return {
            'small_channels_ratio': round((small_count / total_channels * 100), 1),
            'medium_channels_ratio': round((medium_count / total_channels * 100), 1),
            'large_channels_ratio': round((large_count / total_channels * 100), 1),
            'unknown_channels_ratio': round((unknown_count / total_channels * 100), 1)
        }

    def analyze_niche(self, keyword, geo_region='ES'):
        """
        Analizar un nicho específico con todas las mejoras
        """
        print(f"📊 Analizando nicho: '{keyword}'")

        try:
            # Buscar videos
            track_youtube_search(keyword)
            search_request = self.youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                maxResults=10,
                order="relevance",
                publishedAfter=self.date_limit
            )
            search_response = search_request.execute()

            if not search_response['items']:
                print(f"   ❌ No se encontraron videos para '{keyword}'")
                return None

            # Obtener estadísticas y snippet completo
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            track_youtube_videos(keyword, len(video_ids))
            
            stats_request = self.youtube.videos().list(
                part="statistics,snippet",
                id=",".join(video_ids)
            )
            stats_response = stats_request.execute()

            # Calcular métricas básicas
            total_views = sum(int(item['statistics'].get('viewCount', 0))
                            for item in stats_response['items'])
            avg_views = total_views / len(stats_response['items']) if stats_response['items'] else 0

            total_likes = sum(int(item['statistics'].get('likeCount', 0))
                            for item in stats_response['items'])
            total_comments = sum(int(item['statistics'].get('commentCount', 0))
                               for item in stats_response['items'])

            # Análisis avanzado de automatización
            automatizable_analysis = self.analyze_automatizable_advanced(stats_response['items'], geo_region)

            # Análisis de tamaño de canales
            channel_analysis = self.analyze_channel_sizes(stats_response['items'])

            # Compilar resultados
            niche_data = {
                'keyword': keyword,
                'video_count': len(stats_response['items']),
                'avg_views': avg_views,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'automatizable': automatizable_analysis['automatizable_status'],
                'automatizable_ratio': automatizable_analysis['automatizable_ratio'],
                'videos_with_signals': automatizable_analysis['videos_with_signals'],
                'automatizable_signals': automatizable_analysis['automatizable_signals'],
                'small_channels_ratio': channel_analysis['small_channels_ratio'],
                'medium_channels_ratio': channel_analysis['medium_channels_ratio'],
                'large_channels_ratio': channel_analysis['large_channels_ratio'],
                'unknown_channels_ratio': channel_analysis['unknown_channels_ratio']
            }

            self.daily_youtube_requests += 2
            time.sleep(random.uniform(1, 2))

            return niche_data

        except HttpError as e:
            if e.resp.status == 403:
                print("❌ Cuota de YouTube API excedida")
            else:
                print(f"⚠️  Error con '{keyword}': {e}")
            return None

    def generate_report(self, results):
        """Generar reporte en consola"""
        print("\n" + "=" * 80)
        print("📊 REPORTE DE ANÁLISIS DE NICHOS YOUTUBE")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            # Mostrar automatización con señales
            automatizable_status = result.get('automatizable', 'NO')
            automatizable_ratio = result.get('automatizable_ratio', 0)
            automatizable_signals = result.get('automatizable_signals', [])

            if automatizable_status == 'YES':
                auto_icon = "🤖"
            elif automatizable_status == 'PARTIAL':
                auto_icon = "🔄"
            else:
                auto_icon = "👤"

            print(f"\n{i}. 🎯 {result['keyword']}")
            print(f"   📈 Views Promedio: {result['avg_views']:,.0f}")
            
            # Mostrar automatización con señales
            if automatizable_signals:
                signals_str = ', '.join(automatizable_signals)
                print(f"   {auto_icon} Automatizable: {automatizable_status} ({automatizable_ratio}%) | Señales: {signals_str}")
            else:
                print(f"   {auto_icon} Automatizable: {automatizable_status} ({automatizable_ratio}%)")

            # Mostrar distribución de canales
            small_ratio = result.get('small_channels_ratio', 0)
            medium_ratio = result.get('medium_channels_ratio', 0)
            large_ratio = result.get('large_channels_ratio', 0)
            print(f"   📊 Canales: Pequeños {small_ratio}% | Medianos {medium_ratio}% | Grandes {large_ratio}%")

    def export_results(self, results, filename=None):
        """Exportar resultados a CSV y MD"""
        if not results:
            print("❌ No hay resultados para exportar")
            return

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"nichos_youtube_analisis_{timestamp}"

        # Crear carpeta de salida
        out_dir = Path(__file__).resolve().parent / 'out'
        out_dir.mkdir(parents=True, exist_ok=True)

        # Exportar a CSV
        csv_path = out_dir / f"{filename}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'keyword', 'video_count', 'avg_views', 'total_likes', 'total_comments',
                'automatizable', 'automatizable_ratio', 'videos_with_signals', 'automatizable_signals',
                'small_channels_ratio', 'medium_channels_ratio', 'large_channels_ratio', 'unknown_channels_ratio'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'keyword': result['keyword'],
                    'video_count': result['video_count'],
                    'avg_views': result['avg_views'],
                    'total_likes': result['total_likes'],
                    'total_comments': result['total_comments'],
                    'automatizable': result.get('automatizable', 'NO'),
                    'automatizable_ratio': result.get('automatizable_ratio', 0),
                    'videos_with_signals': result.get('videos_with_signals', 0),
                    'automatizable_signals': ','.join(result.get('automatizable_signals', [])),
                    'small_channels_ratio': result.get('small_channels_ratio', 0),
                    'medium_channels_ratio': result.get('medium_channels_ratio', 0),
                    'large_channels_ratio': result.get('large_channels_ratio', 0),
                    'unknown_channels_ratio': result.get('unknown_channels_ratio', 0)
                })

        # Exportar a Markdown
        md_path = out_dir / f"{filename}.md"
        with open(md_path, 'w', encoding='utf-8') as mdfile:
            mdfile.write("# 🎥 ANÁLISIS DE NICHOS YOUTUBE\n")
            mdfile.write("## 📊 Resultados Completos\n\n")
            mdfile.write("=" * 80 + "\n\n")
            
            mdfile.write("### 📅 **Información del Análisis**\n\n")
            mdfile.write(f"- **🕒 Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            mdfile.write(f"- **🎯 Nichos analizados:** {len(results)}\n\n")
            mdfile.write("---\n\n")
            
            mdfile.write("## 🏆 NICHOS ANALIZADOS\n\n")
            
            for i, result in enumerate(results, 1):
                # Automatización con señales
                automatizable_status = result.get('automatizable', 'NO')
                automatizable_ratio = result.get('automatizable_ratio', 0)
                automatizable_signals = result.get('automatizable_signals', [])
                
                if automatizable_status == 'YES':
                    auto_icon = "🤖"
                elif automatizable_status == 'PARTIAL':
                    auto_icon = "🔄"
                else:
                    auto_icon = "👤"

                mdfile.write(f"### {i}. 🎯 **{result['keyword']}**\n\n")
                mdfile.write(f"- **📈 Views Promedio:** {result['avg_views']:,.0f}\n")
                mdfile.write(f"- **{auto_icon} Automatizable:** {automatizable_status} ({automatizable_ratio}%)\n")
                
                # Línea de señales detectadas
                if automatizable_signals:
                    mdfile.write(f"- 🔑 **Señales detectadas:** {', '.join(automatizable_signals)}\n")
                else:
                    mdfile.write(f"- 🔑 **Señales detectadas:** \n")
                
                # Distribución de canales
                small_ratio = result.get('small_channels_ratio', 0)
                medium_ratio = result.get('medium_channels_ratio', 0)
                large_ratio = result.get('large_channels_ratio', 0)
                mdfile.write(f"- 📊 **Distribución de canales:** Pequeños {small_ratio}% | Medianos {medium_ratio}% | Grandes {large_ratio}%\n\n")
                mdfile.write("---\n\n")

        print(f"✅ Resultados exportados: CSV={csv_path} MD={md_path}")

    def run_analysis(self, keywords, geo_region='ES'):
        """Ejecutar análisis completo"""
        print("🎥 INICIANDO ANÁLISIS DE NICHOS YOUTUBE")
        print("=" * 60)

        results = []
        for keyword in keywords:
            if self.daily_youtube_requests >= self.max_youtube_per_day:
                print("⚠️  Límite diario de YouTube API alcanzado")
                break

            result = self.analyze_niche(keyword, geo_region)
            if result:
                results.append(result)

        if results:
            self.generate_report(results)
            self.export_results(results)
        else:
            print("❌ No se obtuvieron resultados")

        return results


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Analizador de Nichos YouTube Mejorado')
    parser.add_argument('--keywords', type=str, help="Keywords separadas por '||'")
    parser.add_argument('--keywords-file', type=str, default='keywords_youtube.txt', 
                       help='Archivo de keywords (una por línea)')
    parser.add_argument('--geo', type=str, default='ES', help='Región (ES, US, MX, etc.)')
    args = parser.parse_args()

    analyzer = NicheAnalyzerYouTube()

    # Obtener keywords
    keywords = []
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split('||') if k.strip()]
    else:
        # Leer desde archivo
        keywords_file = Path(args.keywords_file)
        if keywords_file.exists():
            with keywords_file.open('r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip()]
        else:
            print(f"❌ Archivo {keywords_file} no encontrado")
            return

    if not keywords:
        print("❌ No se proporcionaron keywords")
        return

    # Ejecutar análisis
    analyzer.run_analysis(keywords[:5], args.geo)  # Máximo 5 keywords


if __name__ == "__main__":
    main()
