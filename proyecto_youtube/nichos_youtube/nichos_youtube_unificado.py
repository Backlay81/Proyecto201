"""
(moved) Analizador unificado de nichos — ubicación: proyecto_youtube/nichos_youtube/
Este archivo es una copia funcional del analizador; mantiene PROJECT_ROOT apuntando
al directorio `proyecto_youtube`.
"""

import os
import sys
import csv
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import statistics
import random

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
try:
    import pandas as pd
except ImportError:
    pd = None

# Ajustar PROJECT_ROOT para que apunte a la carpeta `proyecto_youtube`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / 'config'))
sys.path.append(str(PROJECT_ROOT / 'utils'))

try:
    from config import YOUTUBE_API_KEY
except ImportError:
    print("❌ Error: No se pudo importar YOUTUBE_API_KEY desde config.py")
    sys.exit(1)

class SimpleAPIUsageTracker:
    def __init__(self):
        self.usage_file = PROJECT_ROOT / 'utils' / 'api_usage.json'
        self.usage_file.parent.mkdir(exist_ok=True)
    
    def track_usage(self, operation: str, units: int):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            if self.usage_file.exists():
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            if today not in data:
                data[today] = 0
            data[today] += units
            with open(self.usage_file, 'w') as f:
                json.dump(data, f)
            print(f"📊 API Usage: +{units} units ({operation})")
        except Exception as e:
            print(f"⚠️ Warning tracking usage: {e}")
    
    def get_daily_usage(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            if self.usage_file.exists():
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                return data.get(today, 0)
            return 0
        except:
            return 0

class NicheAnalyzerYouTubeUnificado:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.usage_tracker = SimpleAPIUsageTracker()
        self.median_min = int(os.environ.get('MEDIAN_VIEWS_THRESHOLD', 5000))
        self.p75_min = int(os.environ.get('P75_VIEWS_THRESHOLD', 20000))
        self.default_max_results = int(os.environ.get('MAX_RESULTS', 50))

        self.automation_signals_es = [
            "top", "mejores", "ranking", "listado", "comparación", "vs", "versus",
            "cómo hacer", "tutorial", "paso a paso", "fácil", "rápido", "simple",
            "trucos", "tips", "consejos", "guía", "completa", "definitiva",
            "2024", "2025", "actualizado", "último", "nuevo", "tendencia",
            "ganar dinero", "sin experiencia", "desde casa", "automático",
            "compilación", "recopilación", "los más", "trending", "viral"
        ]
        self.automation_signals_en = [
            "top", "best", "ranking", "list", "comparison", "vs", "versus",
            "how to", "tutorial", "step by step", "easy", "quick", "simple",
            "tricks", "tips", "advice", "guide", "complete", "ultimate",
            "2024", "2025", "updated", "latest", "new", "trending",
            "make money", "no experience", "from home", "automatic",
            "compilation", "collection", "most", "viral", "trending"
        ]

        self.monetization_keywords = {
            "afiliacion": ["mejor","mejores","top","ranking","review","reseña","análisis","comparación","vs","versus","comprar","precio","oferta","descuento","amazon","link","descripción","recomiendo","producto","marca","calidad","barato","caro","vale la pena","unboxing","test"],
            "anuncios": ["tutorial","como","cómo","hacer","paso a paso","guía","tips","consejos","trucos","secretos","método","técnica","estrategia","aprender","enseñar","explicar","mostrar","demostrar"],
            "dificil": ["historia","biografía","documental","noticias","política","filosofía","reflexión","opinión personal","experiencia","vida","story","storytime","reacción","react"]
        }

    def search_videos(self, keyword: str, max_results: int = 50, region_code: str = None, relevance_language: str = None) -> List[Dict]:
        try:
            request = self.youtube.search().list(part="snippet", q=keyword, type="video", maxResults=max_results, order="relevance", regionCode=region_code, relevanceLanguage=relevance_language, videoDuration="medium")
            response = request.execute()
            self.usage_tracker.track_usage("search", 100)
            video_ids = [item['id']['videoId'] for item in response['items']]
            stats_request = self.youtube.videos().list(part="statistics,snippet,contentDetails", id=','.join(video_ids))
            stats_response = stats_request.execute()
            self.usage_tracker.track_usage("videos", 1)
            videos = []
            for item in stats_response['items']:
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                if 'viewCount' in stats:
                    video_data = {'id': item['id'], 'title': snippet.get('title',''), 'description': snippet.get('description',''), 'channelTitle': snippet.get('channelTitle',''), 'channelId': snippet.get('channelId',''), 'publishedAt': snippet.get('publishedAt',''), 'tags': snippet.get('tags',[]), 'viewCount': int(stats.get('viewCount',0)), 'likeCount': int(stats.get('likeCount',0)), 'commentCount': int(stats.get('commentCount',0))}
                    videos.append(video_data)
            return videos
        except HttpError as e:
            print(f"❌ Error de API de YouTube: {e}")
            return []
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return []

    def get_channel_info(self, channel_ids: List[str]) -> Dict[str, Dict]:
        try:
            if not channel_ids:
                return {}
            request = self.youtube.channels().list(part="statistics,snippet", id=','.join(list(set(channel_ids))))
            response = request.execute()
            self.usage_tracker.track_usage("channels", 1)
            channels_info = {}
            for item in response['items']:
                channel_id = item['id']
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                channels_info[channel_id] = {'title': snippet.get('title',''), 'subscriber_count': int(stats.get('subscriberCount',0)), 'video_count': int(stats.get('videoCount',0)), 'view_count': int(stats.get('viewCount',0))}
            return channels_info
        except HttpError as e:
            print(f"⚠️  Error obteniendo info de canales: {e}")
            return {}

    def analyze_automation_potential(self, videos: List[Dict]) -> Dict[str, Any]:
        if not videos:
            return {'is_automatizable': False, 'automation_score': 0.0, 'signals_detected': [], 'signal_count': 0, 'analysis_detail': 'No hay videos para analizar'}
        total_signals = 0
        detected_signals = set()
        for video in videos:
            title = video.get('title','').lower(); description = video.get('description','').lower(); tags = [tag.lower() for tag in video.get('tags',[])]
            content_to_check = [title, description] + tags
            for content in content_to_check:
                if not content: continue
                for signal in self.automation_signals_es:
                    if signal in content:
                        detected_signals.add(signal); total_signals += 1
                for signal in self.automation_signals_en:
                    if signal in content:
                        detected_signals.add(signal); total_signals += 1
        automation_score = min(100.0, (total_signals / len(videos)) * 20) if len(videos) > 0 else 0.0
        is_automatizable = automation_score >= 60.0
        signals_list = sorted(detected_signals)
        return {'is_automatizable': is_automatizable, 'automation_score': round(automation_score,1), 'signals_detected': signals_list, 'signal_count': len(signals_list), 'analysis_detail': f"Detectadas {len(signals_list)} señales únicas en {len(videos)} videos"}

    def analyze_channel_sizes(self, videos: List[Dict]) -> Dict[str, Any]:
        if not videos:
            return {'small_channels': 0, 'medium_channels': 0, 'large_channels': 0, 'small_ratio': 0.0, 'medium_ratio': 0.0, 'large_ratio': 0.0, 'analysis_detail': 'No hay videos para analizar'}
        channel_ids = [video['channelId'] for video in videos if 'channelId' in video]
        channels_info = self.get_channel_info(channel_ids)
        small_count = 0; medium_count = 0; large_count = 0
        for video in videos:
            cid = video.get('channelId')
            if cid in channels_info:
                subs = channels_info[cid]['subscriber_count']
                if subs < 50000: small_count += 1
                elif subs < 500000: medium_count += 1
                else: large_count += 1
        total_analyzed = small_count + medium_count + large_count
        if total_analyzed == 0:
            return {'small_channels': 0, 'medium_channels': 0, 'large_channels': 0, 'small_ratio': 0.0, 'medium_ratio': 0.0, 'large_ratio': 0.0, 'analysis_detail': 'No se pudo obtener información de suscriptores'}
        return {'small_channels': small_count, 'medium_channels': medium_count, 'large_channels': large_count, 'small_ratio': round((small_count / total_analyzed) * 100,1), 'medium_ratio': round((medium_count / total_analyzed) * 100,1), 'large_ratio': round((large_count / total_analyzed) * 100,1), 'analysis_detail': f"Analizados {total_analyzed} canales de {len(videos)} videos"}

    def classify_monetization(self, keyword: str) -> Dict[str, Any]:
        keyword_lower = keyword.lower()
        afiliacion_count = sum(1 for word in self.monetization_keywords['afiliacion'] if word in keyword_lower)
        anuncios_count = sum(1 for word in self.monetization_keywords['anuncios'] if word in keyword_lower)
        dificil_count = sum(1 for word in self.monetization_keywords['dificil'] if word in keyword_lower)
        if afiliacion_count > 0 and anuncios_count > 0: monetization_type = 'Afiliación + Anuncios'; monetization_potential = 'Muy Alto'; score = 35
        elif afiliacion_count > 0: monetization_type = 'Solo Afiliación'; monetization_potential = 'Alto'; score = 24
        elif anuncios_count > 0: monetization_type = 'Solo Anuncios'; monetization_potential = 'Medio'; score = 28
        elif dificil_count > 0: monetization_type = 'Difícil Monetizar'; monetization_potential = 'Bajo'; score = 15
        else: monetization_type = 'Solo Anuncios'; monetization_potential = 'Medio'; score = 28
        return {'monetization_type': monetization_type, 'monetization_potential': monetization_potential, 'monetization_score': score, 'keyword_signals': {'afiliacion': afiliacion_count, 'anuncios': anuncios_count, 'dificil': dificil_count}}

    def analyze_video_monetization(self, videos: List[Dict]) -> Dict[str, Any]:
        if not videos: return {'monetizable_count': 0, 'monetizable_ratio': 0.0, 'analysis_detail': 'No hay videos para analizar'}
        monetizable_count = 0
        for video in videos:
            views = video.get('viewCount', 0)
            if views > 10000: monetizable_count += 1
        monetizable_ratio = (monetizable_count / len(videos)) * 100
        return {'monetizable_count': monetizable_count, 'monetizable_ratio': round(monetizable_ratio,1), 'total_videos': len(videos), 'analysis_detail': f"{monetizable_count}/{len(videos)} videos con >10K views"}

    def calculate_saturation_risk(self, videos: List[Dict]) -> Dict[str, Any]:
        if not videos: return {'saturation_risk': 'Unknown', 'saturation_ratio': 0.0, 'analysis_detail': 'No hay videos para analizar'}
        views_list = [video['viewCount'] for video in videos]
        avg_views = statistics.mean(views_list); max_views = max(views_list)
        saturation_ratio = avg_views / max_views if max_views > 0 else 0
        if saturation_ratio >= 0.8: risk_level = '🟢 Bajo'; competition_level = 'low'
        elif saturation_ratio >= 0.4: risk_level = '🟡 Medio'; competition_level = 'medium'
        else: risk_level = '🔴 Alto'; competition_level = 'high'
        return {'saturation_risk': risk_level, 'saturation_ratio': round(saturation_ratio,3), 'competition_level': competition_level, 'avg_views': int(avg_views), 'max_views': int(max_views), 'analysis_detail': f"Ratio saturación: {saturation_ratio:.3f}"}

    def calculate_opportunity_score(self, niche_data: Dict[str, Any]) -> Dict[str, Any]:
        avg_views = niche_data.get('avg_views',0); views_score = min(1.0, avg_views / 100000)
        likes = niche_data.get('total_likes',0); total_views = niche_data.get('total_views',1)
        engagement_score = min(1.0, (likes / total_views) * 1000) if total_views > 0 else 0.5
        competition_scores = {'low':1.0, 'medium':0.7, 'high':0.4, 'very_high':0.1}
        competition_score = competition_scores.get(niche_data.get('competition_level','medium'), 0.5)
        automation_bonus = 0.2 if niche_data.get('is_automatizable', False) else 0.0
        monetization_multipliers = {'Muy Alto':1.2, 'Alto':1.0, 'Medio':0.8, 'Bajo':0.6}
        monetization_multiplier = monetization_multipliers.get(niche_data.get('monetization_potential','Medio'), 0.8)
        final_score = (0.35*views_score + 0.25*competition_score + 0.20*automation_bonus + 0.15*(monetization_multiplier-0.8) + 0.05*engagement_score)
        final_score = max(0, min(1, final_score))
        return {'opportunity_score': round(final_score,3), 'views_score': round(views_score,3), 'competition_score': round(competition_score,3), 'engagement_score': round(engagement_score,3), 'automation_bonus': round(automation_bonus,3), 'monetization_multiplier': round(monetization_multiplier,3)}

    def decide_niche_soft(self, median_views: float, pct75_views: float) -> Tuple[str,str,float]:
        r_med = max(0.0, min(1.0, median_views / float(self.median_min)))
        r_p75 = max(0.0, min(1.0, pct75_views / float(self.p75_min)))
        score = round((r_med + r_p75) / 2 * 100, 1)
        if median_views >= self.median_min and pct75_views >= self.p75_min:
            decision = 'RECOMENDADO'; reason = f"Mediana {median_views:,.0f} ≥ {self.median_min} y P75 {pct75_views:,.0f} ≥ {self.p75_min}"
        elif (median_views >= self.median_min or pct75_views >= self.p75_min) or (median_views >= 0.6*self.median_min and pct75_views >= 0.6*self.p75_min):
            decision = 'EVALUAR'; reason = f"Parcial: Mediana {median_views:,.0f} vs {self.median_min}, P75 {pct75_views:,.0f} vs {self.p75_min}"
        else:
            decision = 'DESCARTAR'; reason = f"Por debajo: Mediana {median_views:,.0f} < {int(0.6*self.median_min)}, P75 {pct75_views:,.0f} < {int(0.6*self.p75_min)}"
        return decision, reason, score

    def analyze_niche(self, keyword: str, region_code: str=None, relevance_language: str=None, max_results: int=50) -> Dict[str, Any]:
        print(f"\n🔍 Analizando nicho: '{keyword}'"); print("="*60)
        videos = self.search_videos(keyword, max_results=max_results, region_code=region_code, relevance_language=relevance_language)
        if not videos: return {'keyword': keyword, 'error': 'No se encontraron videos', 'success': False}
        views_list = [v['viewCount'] for v in videos]; total_views = sum(views_list); avg_views = total_views / len(videos); median_views = statistics.median(views_list)
        sorted_views = sorted(views_list); p75_index = int(0.75 * len(sorted_views)); pct75_views = sorted_views[p75_index] if p75_index < len(sorted_views) else sorted_views[-1]
        max_views = max(views_list); min_views = min(views_list)
        monetization_analysis = self.classify_monetization(keyword); video_monetization = self.analyze_video_monetization(videos)
        saturation_analysis = self.calculate_saturation_risk(videos)
        automation_analysis = self.analyze_automation_potential(videos)
        channel_analysis = self.analyze_channel_sizes(videos)
        decision, reason, base_score = self.decide_niche_soft(median_views, pct75_views)
        niche_data_for_scoring = {'avg_views': avg_views, 'total_views': total_views, 'total_likes': sum(video.get('likeCount',0) for video in videos), 'competition_level': saturation_analysis['competition_level'], 'is_automatizable': automation_analysis['is_automatizable'], 'monetization_potential': monetization_analysis['monetization_potential']}
        opportunity_analysis = self.calculate_opportunity_score(niche_data_for_scoring)
        result = {
            'keyword': keyword, 'region': region_code or 'N/A', 'timestamp': datetime.now().isoformat(), 'success': True,
            'video_count': len(videos), 'total_views': int(total_views), 'avg_views': int(avg_views), 'median_views': int(median_views), 'pct75_views': int(pct75_views), 'max_views': int(max_views), 'min_views': int(min_views),
            'decision': decision, 'reason': reason, 'base_score': base_score, 'opportunity_score': round(opportunity_analysis['opportunity_score']*100,1),
            'monetization_type': monetization_analysis['monetization_type'], 'monetization_potential': monetization_analysis['monetization_potential'], 'monetization_score': monetization_analysis['monetization_score'], 'monetizable_count': video_monetization['monetizable_count'], 'monetizable_ratio': video_monetization['monetizable_ratio'],
            'competition_level': ({'low':'Low','medium':'Medium','high':'High','very_high':'Very High'}.get(saturation_analysis['competition_level'], saturation_analysis['competition_level'].capitalize())), 'saturation_risk': saturation_analysis['saturation_risk'], 'saturation_ratio': saturation_analysis['saturation_ratio'],
            'is_automatizable': automation_analysis['is_automatizable'], 'automation_score': automation_analysis['automation_score'], 'automation_signals': automation_analysis['signal_count'], 'signals_detected': automation_analysis['signals_detected'], 'automatizable_signals': ", ".join(automation_analysis['signals_detected']) if automation_analysis.get('signals_detected') else "",
            'small_channels': channel_analysis['small_channels'], 'medium_channels': channel_analysis['medium_channels'], 'large_channels': channel_analysis['large_channels'], 'small_channels_ratio': channel_analysis['small_ratio'], 'medium_channels_ratio': channel_analysis['medium_ratio'], 'large_channels_ratio': channel_analysis['large_ratio'],
            'views_score': opportunity_analysis['views_score'], 'competition_score': opportunity_analysis['competition_score'], 'engagement_score': opportunity_analysis['engagement_score'], 'automation_bonus': opportunity_analysis['automation_bonus'], 'monetization_multiplier': opportunity_analysis['monetization_multiplier'],
            'automatizable': automation_analysis['is_automatizable'], 'automatizable_count': min(5, automation_analysis['signal_count']), 'riesgo_saturacion': saturation_analysis['saturation_risk'], 'monetizacion': monetization_analysis['monetization_type'], 'score_refinado': base_score
        }
        self._print_analysis_results(result)
        return result

    def _print_analysis_results(self, result: Dict[str, Any]):
        print(f"\n📊 RESULTADOS PARA '{result['keyword']}'"); print("="*60)
        print(f"📹 Videos analizados: {result['video_count']}"); print(f"👀 Views promedio: {result['avg_views']:,}"); print(f"📈 Mediana views: {result['median_views']:,}"); print(f"📊 Percentil 75: {result['pct75_views']:,}"); print(f"🎯 Views máximas: {result['max_views']:,}")
        print(f"\n🎯 DECISIÓN: {result['decision']}"); print(f"📝 Razón: {result['reason']}"); print(f"⭐ Score base: {result['base_score']}/100"); print(f"🎯 Opportunity Score: {result['opportunity_score']:.1f}")
        print(f"\n💰 MONETIZACIÓN:"); print(f"   Tipo: {result['monetization_type']}"); print(f"   Potencial: {result['monetization_potential']}"); print(f"   Videos monetizables: {result['monetizable_count']}/{result['video_count']} ({result['monetizable_ratio']:.1f}%)")
        print(f"\n🤖 AUTOMATIZACIÓN:");
        if result['automation_score'] >= 60.0: status_label = 'YES'
        elif result['automation_score'] > 0: status_label = 'PARTIAL'
        else: status_label = 'NO'
        print(f"   Automatizable: {status_label} ({result['automation_score']:.1f}%) | Señales: {result.get('automatizable_signals','')}")
        print(f"\n⚔️ COMPETENCIA:"); print(f"   Nivel: {result['competition_level']}"); print(f"   Riesgo saturación: {result['saturation_risk']}")
        print(f"\n📺 ANÁLISIS DE CANALES:"); print(f"   Pequeños (<50K): {result['small_channels']} ({result['small_channels_ratio']:.1f}%)"); print(f"   Medianos (50K-500K): {result['medium_channels']} ({result['medium_channels_ratio']:.1f}%)"); print(f"   Grandes (>500K): {result['large_channels']} ({result['large_channels_ratio']:.1f}%)")

    def export_to_csv(self, results: List[Dict[str, Any]], output_file: str):
        if not results: print('⚠️  No hay resultados para exportar'); return
        fieldnames = ['keyword','region','timestamp','video_count','avg_views','median_views','pct75_views','max_views','min_views','total_views','decision','reason','base_score','opportunity_score','monetization_type','monetization_potential','monetization_score','monetizable_count','monetizable_ratio','competition_level','saturation_risk','saturation_ratio','is_automatizable','automation_score','automation_signals','automatizable_signals','small_channels','medium_channels','large_channels','small_channels_ratio','medium_channels_ratio','large_channels_ratio','views_score','competition_score','engagement_score','automation_bonus','monetization_multiplier','automatizable','automatizable_count','riesgo_saturacion','monetizacion','score_refinado']
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames); writer.writeheader();
                for result in results: row = {field: result.get(field,'') for field in fieldnames}; writer.writerow(row)
            print(f"✅ Resultados exportados a: {output_file}")
        except Exception as e:
            print(f"❌ Error exportando CSV: {e}")

    def export_to_markdown(self, results: List[Dict[str, Any]], output_file: str):
        if not results: print('⚠️  No hay resultados para exportar'); return
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 🎥 Análisis de Nichos YouTube - Reporte Unificado\n\n")
                f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total keywords analizadas:** {len(results)}\n\n")
                successful = [r for r in results if r.get('success', True)]; recomendados = [r for r in successful if r.get('decision') == 'RECOMENDADO']; evaluar = [r for r in successful if r.get('decision') == 'EVALUAR']; descartados = [r for r in successful if r.get('decision') == 'DESCARTAR']
                f.write("## 📊 Resumen Ejecutivo\n\n"); f.write(f"- ✅ **Recomendados:** {len(recomendados)}\n"); f.write(f"- ⚠️  **Para evaluar:** {len(evaluar)}\n"); f.write(f"- ❌ **Descartados:** {len(descartados)}\n\n")
                for i, result in enumerate(successful,1):
                    f.write(f"## {i}. {result['keyword']}\n\n")
                    decision = result.get('decision','N/A')
                    if decision == 'RECOMENDADO': f.write("**Status:** ✅ RECOMENDADO\n\n")
                    elif decision == 'EVALUAR': f.write("**Status:** ⚠️ EVALUAR\n\n")
                    else: f.write("**Status:** ❌ DESCARTAR\n\n")
                    f.write("### 📊 Métricas Principales\n\n")
                    f.write(f"- **Videos analizados:** {result.get('video_count',0)}\n")
                    f.write(f"- **Views promedio:** {result.get('avg_views',0):,}\n")
                    f.write(f"- **Mediana views:** {result.get('median_views',0):,}\n")
                    f.write(f"- **Percentil 75:** {result.get('pct75_views',0):,}\n")
                    f.write(f"- **Opportunity Score:** {result.get('opportunity_score',0):.1f}\n\n")
                    auto_status = "✅ Automatizable" if result.get('is_automatizable', False) else "❌ Manual"
                    f.write("### 🤖 Análisis de Automatización\n\n"); f.write(f"- **Status:** {auto_status}\n"); f.write(f"- **Score automatización:** {result.get('automation_score',0):.1f}%\n")
                    signals_txt = result.get('automatizable_signals','')
                    if signals_txt: f.write(f"- **Señales detectadas:** {signals_txt}\n\n")
                    else: f.write(f"- **Señales detectadas:** {result.get('automation_signals',0)}\n\n")
                    f.write("### 📺 Distribución de Canales\n\n")
                    f.write(f"- **Pequeños (<50K subs):** {result.get('small_channels',0)} ({result.get('small_channels_ratio',0):.1f}%)\n")
                    f.write(f"- **Medianos (50K-500K):** {result.get('medium_channels',0)} ({result.get('medium_channels_ratio',0):.1f}%)\n")
                    f.write(f"- **Grandes (>500K):** {result.get('large_channels',0)} ({result.get('large_channels_ratio',0):.1f}%)\n\n")
                    f.write("### ⚔️ Análisis de Competencia\n\n"); f.write(f"- **Nivel competencia:** {result.get('competition_level','N/A')}\n"); f.write(f"- **Riesgo saturación:** {result.get('saturation_risk','N/A')}\n\n")
                    f.write("---\n\n")
            print(f"✅ Reporte Markdown exportado a: {output_file}")
        except Exception as e:
            print(f"❌ Error exportando Markdown: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analizador Unificado de Nichos YouTube')
    parser.add_argument('keywords', nargs='+', help='Keywords a analizar')
    parser.add_argument('--region', default='ES')
    parser.add_argument('--language', default='es')
    parser.add_argument('--output', default='nichos_analysis')
    parser.add_argument('--max-results', type=int, default=50)
    args = parser.parse_args()
    try:
        analyzer = NicheAnalyzerYouTubeUnificado(YOUTUBE_API_KEY)
    except Exception as e:
        print(f"❌ Error inicializando analizador: {e}"); return
    results = []
    for i, keyword in enumerate(args.keywords,1):
        try:
            result = analyzer.analyze_niche(keyword=keyword, region_code=args.region, relevance_language=args.language, max_results=args.max_results)
            if result.get('success', False): results.append(result)
            else: print(f"⚠️  Error analizando '{keyword}': {result.get('error','Unknown error')}")
        except Exception as e:
            print(f"❌ Error inesperado analizando '{keyword}': {e}")
        if i < len(args.keywords): time.sleep(1)
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = PROJECT_ROOT / 'out'
        try: out_dir.mkdir(parents=True, exist_ok=True)
        except Exception: pass
        csv_file = str(out_dir / f"{args.output}_{timestamp}.csv"); md_file = str(out_dir / f"{args.output}_{timestamp}.md")
        analyzer.export_to_csv(results, csv_file); analyzer.export_to_markdown(results, md_file)
        print(f"\n✅ ANÁLISIS COMPLETADO\n📊 {len(results)} nichos analizados exitosamente\n💾 Archivos generados:\n   - CSV: {csv_file}\n   - MD: {md_file}")
    else:
        print('\n❌ No se pudieron analizar nichos')

if __name__ == '__main__':
    main()
