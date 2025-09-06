"""
buscar_canales_youtube.py
Standalone script to find and analyze YouTube channels for given keywords.

Requirements:
- --keyword or --keywords-file input
- Uses YouTube Data API (search.list + channels.list)
- Optional analysis of recent N videos per channel
- Outputs: ranking printed, CSV, Parquet (if pandas+pyarrow), Markdown report

This script is independent and does not import or modify other project scripts.
"""
import os
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import random

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except Exception:
    print("Error: googleapiclient is required. Install google-api-python-client.")
    raise

try:
    import pandas as pd
except Exception:
    pd = None

PROJECT_ROOT = Path(__file__).resolve().parent
OUT_DIR = PROJECT_ROOT / 'out'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_youtube(api_key: str):
    return build('youtube', 'v3', developerKey=api_key)


def search_videos_get_channels(youtube, keyword: str, max_results: int = 50) -> List[str]:
    """Search videos for a keyword and return unique channelIds."""
    try:
        req = youtube.search().list(
            part='snippet', q=keyword, type='video', maxResults=max_results, order='relevance'
        )
        resp = req.execute()
        # preserve order of appearance in search results and deduplicate
        seen = set()
        channel_ids = []
        for item in resp.get('items', []):
            cid = item.get('snippet', {}).get('channelId')
            if cid and cid not in seen:
                seen.add(cid)
                channel_ids.append(cid)
        return channel_ids
    except HttpError as e:
        print(f"YouTube API error searching '{keyword}': {e}")
        return []


def get_channels_info(youtube, channel_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Get channel statistics for a list of channel IDs. Returns dict by channelId."""
    if not channel_ids:
        return {}

    results = {}
    # channels.list accepts up to 50 ids per call
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        try:
            req = youtube.channels().list(part='snippet,statistics', id=','.join(batch))
            resp = req.execute()
            for item in resp.get('items', []):
                cid = item['id']
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                results[cid] = {
                    'channelId': cid,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'publishedAt': snippet.get('publishedAt', ''),
                    'subscriberCount': int(stats.get('subscriberCount', 0)) if stats.get('subscriberCount') else None,
                    'videoCount': int(stats.get('videoCount', 0)) if stats.get('videoCount') else None,
                    'viewCount': int(stats.get('viewCount', 0)) if stats.get('viewCount') else None,
                }
        except HttpError as e:
            print(f"YouTube API error fetching channels: {e}")
    return results


def get_recent_videos_stats(youtube, channel_id: str, max_videos: int = 5) -> Dict[str, Any]:
    """Optional: fetch recent videos for a channel and compute avg/median views and basic signals."""
    try:
        # search by channelId ordered by date
        req = youtube.search().list(part='id', channelId=channel_id, type='video', order='date', maxResults=max_videos)
        resp = req.execute()
        video_ids = [item['id']['videoId'] for item in resp.get('items', []) if item.get('id', {}).get('videoId')]
        if not video_ids:
            return {'recent_count': 0, 'avg_views': None, 'median_views': None}

        stats_req = youtube.videos().list(part='statistics,snippet', id=','.join(video_ids))
        stats_resp = stats_req.execute()
        views = []
        titles = []
        for v in stats_resp.get('items', []):
            s = v.get('statistics', {})
            views.append(int(s.get('viewCount', 0)))
            titles.append(v.get('snippet', {}).get('title', ''))

        import statistics
        avg_v = statistics.mean(views) if views else None
        med_v = statistics.median(views) if views else None
        return {'recent_count': len(views), 'avg_views': avg_v, 'median_views': med_v, 'titles': titles}
    except HttpError as e:
        print(f"YouTube API error fetching recent videos for {channel_id}: {e}")
        return {'recent_count': 0, 'avg_views': None, 'median_views': None}


def export_outputs(rows: List[Dict[str, Any]], prefix: str):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = OUT_DIR / f"{prefix}_{timestamp}.csv"
    md_path = OUT_DIR / f"{prefix}_{timestamp}.md"

    # Export CSV
    try:
        if pd is not None:
            df = pd.DataFrame(rows)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            # Try parquet if pyarrow available
            try:
                df.to_parquet(OUT_DIR / f"{prefix}_{timestamp}.parquet")
            except Exception:
                pass
        else:
            # Fallback CSV writer
            import csv
            keys = set().union(*(r.keys() for r in rows)) if rows else []
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(keys))
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)
        print(f"✅ Resultados exportados a: {csv_path}")
    except Exception as e:
        print(f"Error exportando CSV: {e}")

    # Export Markdown report
    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Informe de canales - {prefix}\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total canales: {len(rows)}\n\n")
            for i, r in enumerate(rows, 1):
                f.write(f"## {i}. {r.get('title','-')} ({r.get('channelId','-')})\n\n")
                f.write(f"- Subscribers: {r.get('subscriberCount') or 'N/A'}\n")
                f.write(f"- Total views: {r.get('viewCount') or 'N/A'}\n")
                f.write(f"- Videos count: {r.get('videoCount') or 'N/A'}\n")
                if r.get('recent_count') is not None:
                    f.write(f"- Recent videos analyzed: {r.get('recent_count')}\n")
                    f.write(f"- Recent avg views: {r.get('avg_views') or 'N/A'}\n")
                    f.write(f"- Recent median views: {r.get('median_views') or 'N/A'}\n")
                f.write('\n---\n\n')
        print(f"✅ Reporte Markdown exportado a: {md_path}")
    except Exception as e:
        print(f"Error exportando Markdown: {e}")


def main():
    parser = argparse.ArgumentParser(description='Buscar y analizar canales de YouTube por keyword')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--keyword', help='Keyword única a buscar', type=str)
    group.add_argument('--keywords-file', help='Archivo con keywords (una por línea)', type=str)
    parser.add_argument('--mode', help='Modo de selección de canales: relevance|top|random', choices=['relevance','top','random'], default='relevance')
    parser.add_argument('--api-key', help='YouTube API key (o ENV YOUTUBE_API_KEY)')
    parser.add_argument('--max-results', help='Videos a buscar por keyword (search.list maxResults)', type=int, default=50)
    parser.add_argument('--recent', help='Analizar N videos recientes por canal (opcional)', type=int, default=0)
    parser.add_argument('--sort-by', help='Ordenar ranking por: subs|views (default subs)', choices=['subs','views'], default='subs')
    parser.add_argument('--output-prefix', help='Prefijo para archivos de salida', default='buscar_canales')

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print('Error: Se requiere YOUTUBE_API_KEY en env o --api-key')
        sys.exit(1)

    keywords = []
    if args.keyword:
        keywords = [args.keyword]
    else:
        with open(args.keywords_file, 'r', encoding='utf-8') as f:
            keywords = [l.strip() for l in f if l.strip()]

    youtube = build_youtube(api_key)

    aggregated_channels = {}

    for kw in keywords:
        print(f"\n🔎 Buscando canales para: {kw}")
        print(f"  → Modo seleccionado: {args.mode}")
        # Extract channel IDs preserving relevance order
        channel_ids = search_videos_get_channels(youtube, kw, max_results=args.max_results)
        print(f"  → Canales únicos encontrados (pre-selección): {len(channel_ids)}")

        # Selection logic per mode
        if args.mode in ('relevance', 'random'):
            ids_for_stats = list(channel_ids)
            if args.mode == 'random':
                random.shuffle(ids_for_stats)
            # limit to max_results before fetching stats to save API units
            ids_for_stats = ids_for_stats[:args.max_results]
            print(f"  → Canales a consultar (limitados por max-results): {len(ids_for_stats)}")
            channels_info = get_channels_info(youtube, ids_for_stats)
            for cid, info in channels_info.items():
                aggregated_channels[cid] = info
        else:  # mode == 'top'
            # Need stats for all found channel_ids to select top by subscribers
            channels_info_all = get_channels_info(youtube, channel_ids)
            sorted_channels = sorted(
                channels_info_all.values(),
                key=lambda x: (x.get('subscriberCount') or 0),
                reverse=True
            )
            top_n = sorted_channels[:args.max_results]
            print(f"  → Canales consultados: {len(channels_info_all)} | Seleccionando top {len(top_n)} por subs")
            for info in top_n:
                cid = info['channelId']
                aggregated_channels[cid] = info
        # Small delay to be polite
        time.sleep(1)

    rows = []
    for cid, info in aggregated_channels.items():
        row = dict(info)
        if args.recent and args.recent > 0:
            recent = get_recent_videos_stats(youtube, cid, max_videos=args.recent)
            row.update(recent)
        rows.append(row)

    # Ranking
    if args.sort_by == 'subs':
        rows_sorted = sorted(rows, key=lambda r: (r.get('subscriberCount') or 0), reverse=True)
    else:
        rows_sorted = sorted(rows, key=lambda r: (r.get('viewCount') or 0), reverse=True)

    # Print top 20
    print('\n🏆 Ranking (top 20):')
    for i, r in enumerate(rows_sorted[:20], 1):
        print(f"{i}. {r.get('title','-')} | subs: {r.get('subscriberCount') or 'N/A'} | views: {r.get('viewCount') or 'N/A'} | videos: {r.get('videoCount') or 'N/A'}")

    export_outputs(rows_sorted, args.output_prefix)


if __name__ == '__main__':
    main()
