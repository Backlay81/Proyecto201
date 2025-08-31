"""
Script para consultar y analizar videos de YouTube.
Autor: Proyecto 201 digital
Fecha: 28/08/2025
"""

import sys
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Añadir la carpeta credentials al path para importar config
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
from config import YOUTUBE_API_KEY


def search_videos(query, max_results=10):
    """
    Busca videos en YouTube por palabra clave
    """
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Buscar videos
        search_request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            order="relevance"
        )
        
        search_response = search_request.execute()
        
        # Obtener IDs de videos para estadísticas
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        # Obtener estadísticas de los videos
        stats_request = youtube.videos().list(
            part="statistics,contentDetails",
            id=",".join(video_ids)
        )
        
        stats_response = stats_request.execute()
        
        # Combinar datos
        results = []
        for i, item in enumerate(search_response['items']):
            video_data = {
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'video_id': item['id']['videoId'],
                'views': int(stats_response['items'][i]['statistics'].get('viewCount', 0)),
                'likes': int(stats_response['items'][i]['statistics'].get('likeCount', 0)),
                'comments': int(stats_response['items'][i]['statistics'].get('commentCount', 0)),
                'duration': stats_response['items'][i]['contentDetails']['duration']
            }
            results.append(video_data)
        
        return results
        
    except HttpError as e:
        print(f"Error de API de YouTube: {e}")
        return []


def analyze_niche(keyword):
    """
    Analiza un nicho específico en YouTube
    """
    print(f"🔍 Analizando nicho: {keyword}")
    
    videos = search_videos(keyword, max_results=20)
    
    if not videos:
        print("❌ No se encontraron videos")
        return None
    
    # Calcular métricas
    total_views = sum(v['views'] for v in videos)
    avg_views = total_views / len(videos)
    max_views = max(v['views'] for v in videos)
    
    print(f"📊 Resultados para '{keyword}':")
    print(f"   Videos encontrados: {len(videos)}")
    print(f"   Views promedio: {avg_views:,.0f}")
    print(f"   Views máximas: {max_views:,.0f}")
    print(f"   Views totales: {total_views:,.0f}")
    
    # Mostrar top 5 videos
    print(f"\n🏆 Top 5 videos más populares:")
    sorted_videos = sorted(videos, key=lambda x: x['views'], reverse=True)[:5]
    
    for i, video in enumerate(sorted_videos, 1):
        print(f"   {i}. {video['title'][:50]}... - {video['views']:,} views")
    
    return {
        'keyword': keyword,
        'video_count': len(videos),
        'avg_views': avg_views,
        'max_views': max_views,
        'total_views': total_views,
        'top_videos': sorted_videos[:5]
    }


def main():
    """
    Función principal para probar el script
    """
    print("🚀 Iniciando análisis de YouTube...")
    
    # Palabras clave de prueba
    test_keywords = [
        "finanzas personales",
        "tutorial python",
        "marketing digital"
    ]
    
    results = []
    for keyword in test_keywords:
        result = analyze_niche(keyword)
        if result:
            results.append(result)
        print("-" * 50)
    
    print(f"\n✅ Análisis completado. Procesados {len(results)} nichos.")


if __name__ == "__main__":
    main()
