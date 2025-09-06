"""
buscar_canales_youtube.py (moved)
Ubicación: proyecto_youtube/canales_youtube/
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

# Ajustar PROJECT_ROOT para que apunte a la carpeta `proyecto_youtube`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / 'out'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_youtube(api_key: str):
    return build('youtube', 'v3', developerKey=api_key)


def search_videos_get_channels(youtube, keyword: str, max_results: int = 50) -> List[str]:
    """Search videos for a keyword and return up to max_results unique channelIds.

    The YouTube API returns up to 50 results per page. This function will paginate
    through search results (up to a reasonable limit) to try to collect enough
    unique channel IDs. We stop when we have collected `max_results` unique
    channels or when there are no more pages.
    """
    try:
        seen = set()
        channel_ids = []
        page_token = None
        # We'll allow up to 5 pages to avoid excessive usage (5 * 50 = 250 videos)
        pages_remaining = 5

        while pages_remaining > 0 and len(seen) < max_results:
            req = youtube.search().list(
                part='snippet', q=keyword, type='video', maxResults=50, order='relevance', pageToken=page_token
            )
            resp = req.execute()

            for item in resp.get('items', []):
                cid = item.get('snippet', {}).get('channelId')
                if cid and cid not in seen:
                    seen.add(cid)
                    channel_ids.append(cid)
                    if len(seen) >= max_results:
                        break

            page_token = resp.get('nextPageToken')
            if not page_token:
                break
            pages_remaining -= 1
            # small polite delay
            time.sleep(0.2)

        return channel_ids[:max_results]
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
        descriptions = []
        for v in stats_resp.get('items', []):
            s = v.get('statistics', {})
            views.append(int(s.get('viewCount', 0)))
            titles.append(v.get('snippet', {}).get('title', ''))
            descriptions.append(v.get('snippet', {}).get('description', ''))

        import statistics
        avg_v = statistics.mean(views) if views else None
        med_v = statistics.median(views) if views else None
        return {'recent_count': len(views), 'avg_views': avg_v, 'median_views': med_v, 'titles': titles, 'descriptions': descriptions}
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
            # Group by competencia_tipo for the markdown report
            directos = [r for r in rows if r.get('competencia_tipo') == 'Directa']
            indirectos = [r for r in rows if r.get('competencia_tipo') == 'Indirecta']

            f.write('## Competencia directa (mismo nicho)\n\n')
            for i, r in enumerate(directos, 1):
                f.write(f"### {i}. {r.get('title','-')} ({r.get('channelId','-')})\n\n")
                f.write(f"- Subscribers: {r.get('subscriberCount') or 'N/A'}\n")
                f.write(f"- Total views: {r.get('viewCount') or 'N/A'}\n")
                f.write(f"- Videos count: {r.get('videoCount') or 'N/A'}\n")
                if r.get('recent_count') is not None:
                    f.write(f"- Recent videos analyzed: {r.get('recent_count')}\n")
                    f.write(f"- Recent avg views: {r.get('avg_views') or 'N/A'}\n")
                    f.write(f"- Recent median views: {r.get('median_views') or 'N/A'}\n")
                if r.get('origin_keywords'):
                    f.write(f"- Origin keywords: {r.get('origin_keywords')}\n")
                f.write('\n---\n\n')

            f.write('## Competencia indirecta (nichos cercanos)\n\n')
            for i, r in enumerate(indirectos, 1):
                f.write(f"### {i}. {r.get('title','-')} ({r.get('channelId','-')})\n\n")
                f.write(f"- Subscribers: {r.get('subscriberCount') or 'N/A'}\n")
                f.write(f"- Total views: {r.get('viewCount') or 'N/A'}\n")
                f.write(f"- Videos count: {r.get('videoCount') or 'N/A'}\n")
                if r.get('recent_count') is not None:
                    f.write(f"- Recent videos analyzed: {r.get('recent_count')}\n")
                    f.write(f"- Recent avg views: {r.get('avg_views') or 'N/A'}\n")
                    f.write(f"- Recent median views: {r.get('median_views') or 'N/A'}\n")
                if r.get('origin_keywords'):
                    f.write(f"- Origin keywords: {r.get('origin_keywords')}\n")
                f.write('\n---\n\n')
        print(f"✅ Reporte Markdown exportado a: {md_path}")
    except Exception as e:
        print(f"Error exportando Markdown: {e}")


def main():
    parser = argparse.ArgumentParser(description='Buscar y analizar canales de YouTube por keyword')
    group = parser.add_mutually_exclusive_group(required=True)
    # Allow multiple --keyword occurrences (action='append') so user can pass several keywords directly
    group.add_argument('--keyword', help='Keyword a buscar (puedes usar --keyword varias veces)', type=str, action='append')
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
        # args.keyword is a list when action='append' is used
        keywords = [k.strip() for k in args.keyword if k and k.strip()]
    else:
        with open(args.keywords_file, 'r', encoding='utf-8') as f:
            keywords = [l.strip() for l in f if l.strip()]

    youtube = build_youtube(api_key)

    # Try to initialize DB if available
    try:
        from proyecto_youtube.db.utils import init_db, save_result
        from proyecto_youtube.db.session import SessionLocal
        init_db()
        db_session = SessionLocal()
        db_enabled = True
    except Exception:
        db_enabled = False

    aggregated_channels = {}

    # For each keyword produce a separate output with up to --max-results channels
    for kw in keywords:
        print(f"\n🔎 Buscando canales para: {kw}")
        print(f"  → Modo seleccionado: {args.mode}")
        # Extract channel IDs preserving relevance order
        channel_ids = search_videos_get_channels(youtube, kw, max_results=args.max_results)
        print(f"  → Canales únicos encontrados (pre-selección): {len(channel_ids)}")

        # Selection logic per mode (this yields the list of channelIds/info for this keyword)
        ids_for_stats = []
        channels_info = {}

        if args.mode in ('relevance', 'random'):
            ids_for_stats = list(channel_ids)
            if args.mode == 'random':
                random.shuffle(ids_for_stats)
            # limit to max_results before fetching stats to save API units
            ids_for_stats = ids_for_stats[:args.max_results]
            print(f"  → Canales a consultar (limitados por max-results): {len(ids_for_stats)}")
            channels_info = get_channels_info(youtube, ids_for_stats)

            # preserve requested order (ids_for_stats) when building per-keyword rows
            per_kw_infos = [channels_info[cid] for cid in ids_for_stats if cid in channels_info]

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
            per_kw_infos = top_n

        # Small delay to be polite
        time.sleep(1)

        # For this keyword, prepare rows (and optionally fetch recent stats)
        rows_kw = []
        # detection keywords
        signals_es = ["cuento","cuentos","historia","historias","niños","infantil","interactivo","elige tu propia aventura"]
        signals_en = ["story","stories","interactive","choose your own adventure","kids","bedtime","fairy tale"]

        for info in per_kw_infos:
            row = dict(info)
            # fetch recent titles/descriptions to classify (if requested)
            recent = {}
            if args.recent and args.recent > 0:
                recent = get_recent_videos_stats(youtube, row.get('channelId'), max_videos=args.recent)
                row.update(recent)

            # Build text corpus from recent titles and descriptions if available, else use channel description
            corpus = ''
            if row.get('titles'):
                corpus += ' '.join(row.get('titles', []))
            if row.get('descriptions'):
                corpus += ' ' + ' '.join(row.get('descriptions', []))
            if not corpus:
                corpus = (row.get('description') or '')

            corpus_l = corpus.lower()
            competencia_tipo = 'Indirecta'
            # simple detection: if any ES or EN signal appears -> Directa
            if any(s in corpus_l for s in signals_es) or any(s in corpus_l for s in signals_en):
                competencia_tipo = 'Directa'

            row['competencia_tipo'] = competencia_tipo
            rows_kw.append(row)

            # Add to aggregated collection as well (track recurrence count and origin keywords)
            cid = row.get('channelId')
            if cid:
                if cid not in aggregated_channels:
                    # store the full row (so competencia_tipo and recent stats when present are preserved)
                    aggregated_channels[cid] = dict(row)
                    # keep a set of origin keywords for later export
                    aggregated_channels[cid]['origin_keywords'] = set([kw])
                    aggregated_channels[cid]['occurrences'] = 1
                else:
                    # increment occurrence
                    aggregated_channels[cid].setdefault('occurrences', 1)
                    aggregated_channels[cid]['occurrences'] += 1
                    # merge origin keyword
                    aggregated_channels[cid].setdefault('origin_keywords', set()).add(kw)
                    # if any encounter classifies as Directa, keep Directa
                    prev_comp = aggregated_channels[cid].get('competencia_tipo')
                    if prev_comp != 'Directa' and row.get('competencia_tipo') == 'Directa':
                        aggregated_channels[cid]['competencia_tipo'] = 'Directa'
                # Save to DB per canal if available
                if db_enabled:
                    try:
                        save_result(db_session, kw, row)
                    except Exception:
                        pass

        # Export per-keyword outputs (CSV + MD) so user gets up to N channels per keyword
        # Build a safe prefix from keyword
        safe_kw = ''.join(c if (c.isalnum() or c in (' ', '_')) else '_' for c in kw).strip().replace(' ', '_')
        prefix = f"{args.output_prefix}_{safe_kw}"
        export_outputs(rows_kw, prefix)

    # After all keywords processed export aggregated results as before
    rows = []
    for cid, info in aggregated_channels.items():
        row = dict(info)
        # occurrences -> recurrente if >1
        occ = info.get('occurrences', 1)
        row['recurrente'] = True if occ > 1 else False
        # ensure competencia_tipo exists (default Indirecta)
        row['competencia_tipo'] = info.get('competencia_tipo', 'Indirecta')
        # serialize origin_keywords set to comma-separated string for CSV/MD
        ok = info.get('origin_keywords')
        if isinstance(ok, set):
            row['origin_keywords'] = ','.join(sorted(ok))
        elif isinstance(ok, (list, tuple)):
            row['origin_keywords'] = ','.join(ok)
        else:
            row['origin_keywords'] = ok or ''

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
