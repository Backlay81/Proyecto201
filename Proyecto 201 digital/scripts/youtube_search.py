"""
Script para consultar y analizar videos de YouTube.
Autor: Proyecto 201 digital
Fecha: 28/08/2025
"""

import sys
import json
from datetime import datetime
import statistics
# --- CONFIGURACIÓN DE CUOTA Y USO ---
API_DAILY_LIMIT = 10000  # Cambia este valor si tu cuota diaria es diferente
USAGE_FILE = "youtube_api_usage.json"

def load_api_usage():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == today:
            return data["units"]
        else:
            return 0
    except Exception:
        return 0

def save_api_usage(units):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today, "units": units}, f)

def print_api_usage(units):
    print(f"\n🔢 Unidades gastadas hoy: {units:,} / {API_DAILY_LIMIT:,}  |  Quedan: {API_DAILY_LIMIT-units:,}")
    if units > API_DAILY_LIMIT * 0.9:
        print("⚠️  ¡Cuidado! Estás cerca del límite diario de la API de YouTube.")
    elif units > API_DAILY_LIMIT:
        print("❌ Has superado el límite diario de la API de YouTube. Detén el script para evitar bloqueos.")

# Inicializar contador global de unidades usadas (persistente por día)
api_units_used = load_api_usage()
import os
import csv
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import random
import argparse
from pathlib import Path
import shutil
try:
    import pandas as pd
except Exception:
    pd = None


# Añadir la carpeta credentials al path para importar config
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials"))
from config import YOUTUBE_API_KEY


# ---------------- CONFIGURABLE THRESHOLDS ----------------
MEDIAN_VIEWS_THRESHOLD = int(os.environ.get('MEDIAN_VIEWS_THRESHOLD', 5000))
P75_VIEWS_THRESHOLD = int(os.environ.get('P75_VIEWS_THRESHOLD', 20000))

# Backwards-friendly names requested
MEDIAN_MIN = MEDIAN_VIEWS_THRESHOLD
PCT75_MIN = P75_VIEWS_THRESHOLD


# TODO: Decisión suave + score combinado (mediana/P75)
def decide_niche_soft(median_views: float, pct75_views: float,
                      median_min: int, p75_min: int) -> tuple[str, str, float]:
    """
    Devuelve (decision, reason, score_0_100).
    Regla:
      - RECOMENDADO si median >= median_min y p75 >= p75_min
      - EVALUAR si cumple al menos uno de los dos o ambos >= 60% del umbral
      - DESCARTAR si ambos por debajo del 60% del umbral
    Score (0-100): media de dos ratios recortados a 1, ponderada 50/50.
    """
    # ratios recortados [0,1]
    r_med = max(0.0, min(1.0, median_views / float(median_min if median_min else 1)))
    r_p75 = max(0.0, min(1.0, pct75_views / float(p75_min if p75_min else 1)))
    score = round((r_med + r_p75) / 2 * 100, 1)

    if median_views >= median_min and pct75_views >= p75_min:
        decision = "RECOMENDADO"
        reason = (f"Mediana {median_views:,.0f} ≥ {median_min} y "
                  f"P75 {pct75_views:,.0f} ≥ {p75_min}")
    elif (median_views >= median_min or pct75_views >= p75_min) or \
         (median_views >= 0.6*median_min and pct75_views >= 0.6*p75_min):
        decision = "EVALUAR"
        reason = (f"Parcial: Mediana {median_views:,.0f} vs {median_min}, "
                  f"P75 {pct75_views:,.0f} vs {p75_min}")
    else:
        decision = "DESCARTAR"
        reason = (f"Por debajo: Mediana {median_views:,.0f} < {int(0.6*median_min)}* "
                  f"y P75 {pct75_views:,.0f} < {int(0.6*p75_min)}* (zona baja)")
    return decision, reason, score


def decide_niche(median_views: float, pct75_views: float) -> tuple[str, str]:
    """
    Devuelve (decision, reason)
    decision in {"RECOMENDADO", "EVALUAR", "DESCARTAR"}
    """
    if median_views > MEDIAN_MIN and pct75_views > PCT75_MIN:
        return "RECOMENDADO", (
            f"Mediana {median_views:,.0f} > {MEDIAN_MIN} y P75 {pct75_views:,.0f} > {PCT75_MIN}"
        )
    if median_views <= MEDIAN_MIN:
        return "DESCARTAR", (
            f"Mediana {median_views:,.0f} <= {MEDIAN_MIN} (demanda general baja)"
        )
    # median > MEDIAN_MIN pero P75 no alcanza el mínimo
    return "EVALUAR", (
        f"Mediana {median_views:,.0f} > {MEDIAN_MIN} pero P75 {pct75_views:,.0f} <= {PCT75_MIN}"
    )



def clasificar_monetizacion(keyword):
    """
    Clasifica el potencial de monetización de un nicho (versión bilingüe mejorada)
    """
    # Diccionario bilingüe para afiliación (ES/EN)
    afiliacion_es = [
        "pienso", "mejores productos", "review", "comparativa", "mejor cámara", 
        "gadgets", "amazon", "descuento", "producto", "comprar", "precio",
        "recomendación", "análisis", "unboxing", "test", "vs", "opinión",
        "cual comprar", "marca", "calidad", "barato", "oferta", "promoción",
        "top 10", "ranking", "equipamiento", "herramientas", "accesorios",
        "comprar", "oferta", "precio", "cupón", "descuento", "amazon", 
        "link en la descripción"
    ]
    
    afiliacion_en = [
        "buy", "deal", "price", "coupon", "discount", "amazon", 
        "link in description", "referral", "affiliate", "sponsored",
        "best", "review", "comparison", "better", "gadgets", "product",
        "recommendation", "analysis", "unboxing", "test", "vs", "opinion",
        "which to buy", "brand", "quality", "cheap", "offer", "promotion",
        "top 10", "ranking", "equipment", "tools", "accessories"
    ]
    
    # Diccionario bilingüe para anuncios de alto CPM (ES/EN)
    anuncios_es = [
        "finanzas", "criptomonedas", "bitcoin", "invertir", "banca", "seguros", 
        "psicología", "coaching", "salud", "educación", "tecnología", "marketing", 
        "negocio", "inversión", "curso", "formación", "desarrollo personal", 
        "dinero", "emprendimiento", "startup", "forex", "trading", "bolsa",
        "hipoteca", "prestamo", "ahorro", "jubilación", "terapia", "medicina"
    ]
    
    anuncios_en = [
        "finance", "cryptocurrency", "crypto", "bitcoin", "invest", "banking", "insurance",
        "psychology", "coaching", "health", "education", "technology", "marketing",
        "business", "investment", "course", "training", "personal development",
        "money", "entrepreneurship", "startup", "forex", "trading", "stock",
        "mortgage", "loan", "savings", "retirement", "therapy", "medicine",
        "credit card", "real estate", "side hustle", "passive income"
    ]
    
    keyword_lower = keyword.lower()
    
    # Combinar palabras de ambos idiomas
    afiliacion_all = afiliacion_es + afiliacion_en
    anuncios_all = anuncios_es + anuncios_en
    
    # Verificar si contiene palabras de afiliación
    afiliable = any(palabra in keyword_lower for palabra in afiliacion_all)
    
    # Verificar si contiene palabras de anuncios de alto CPM
    anunciable = any(palabra in keyword_lower for palabra in anuncios_all)
    
    if afiliable and anunciable:
        return "Afiliación + Anuncios"
    elif afiliable:
        return "Solo Afiliación"
    elif anunciable:
        return "Solo Anuncios"
    else:
        return "Difícil Monetizar"


def is_automatizable(title):
    """
    Determina si un video es automatizable con IA (versión refinada)
    """
    keywords_automatizables = [
        "review", "top", "mejores", "comparativa", "guía", "tutorial", 
        "introducción", "opinión", "análisis", "explicación", "cómo funciona", 
        "historia de", "beneficios", "desventajas", "pros y contras",
        "qué es", "tipos de", "características", "ventajas", "lista",
        "ranking", "selección", "recomendaciones", "consejos", "curso",
        "aprende", "enseñar", "método", "estrategia", "técnica", "proceso"
    ]
    
    # Penalizar contenido manual/personal (expandido)
    keywords_no_automatizables = [
        "vlog", "mi experiencia", "reacción", "gameplay", "en vivo",
        "mi historia", "testimonio", "día en mi vida", "rutina",
        "behind the scenes", "challenge", "tag", "q&a", "manualidades",
        "diy", "craft", "mi caso", "personal", "conmigo", "yo hago",
        "mi método", "así lo hago", "mi forma", "unboxing", "haul"
    ]
    
    title_lower = title.lower()
    
    # Si contiene palabras no automatizables, es false
    if any(kw in title_lower for kw in keywords_no_automatizables):
        return False
    
    # Si contiene palabras automatizables, es true
    return any(kw in title_lower for kw in keywords_automatizables)


def analizar_titulos_monetizacion(videos):
    """
    Analiza los títulos de los videos para detectar patrones de monetización (versión bilingüe)
    """
    afiliacion_count = 0
    anuncios_count = 0
    
    # Palabras de afiliación bilingües
    afiliacion_words_es = ["review", "mejor", "comparativa", "recomiendo", "análisis", "opinión", "top", "ranking", "producto", "comprar"]
    afiliacion_words_en = ["review", "best", "comparison", "recommend", "analysis", "opinion", "top", "ranking", "product", "buy", "deal", "affiliate"]
    afiliacion_words = afiliacion_words_es + afiliacion_words_en
    
    # Palabras de anuncios altos bilingües
    anuncios_words_es = ["finanzas", "dinero", "inversión", "negocio", "curso", "coaching", "bitcoin", "crypto", "trading", "emprender"]
    anuncios_words_en = ["finance", "money", "investment", "business", "course", "coaching", "bitcoin", "crypto", "trading", "entrepreneur", "credit", "loan", "insurance"]
    anuncios_words = anuncios_words_es + anuncios_words_en
    
    for video in videos:
        title = video['title'].lower()
        
        # Contar videos con potencial de afiliación
        if any(word in title for word in afiliacion_words):
            afiliacion_count += 1
        
        # Contar videos con potencial de anuncios altos
        if any(word in title for word in anuncios_words):
            anuncios_count += 1
    
    # TODO: Arreglar ratio monetizable para no superar 100%
    total_monetizables = afiliacion_count + anuncios_count
    
    # Clamp to avoid counting videos twice
    total_monetizables = min(total_monetizables, len(videos))
    
    return {
        'videos_afiliacion': afiliacion_count,
        'videos_anuncios': anuncios_count,
        'videos_monetizables': total_monetizables,
        'porcentaje_afiliacion': round((afiliacion_count / max(1, len(videos))) * 100, 1),
        'porcentaje_anuncios': round((anuncios_count / max(1, len(videos))) * 100, 1),
        'porcentaje_monetizables': round((total_monetizables / max(1, len(videos))) * 100, 1)
    }


def calcular_score_monetizacion(tipo_monetizacion, analisis_titulos):
    """
    Calcula un score de monetización del 1-10
    """
    base_scores = {
        "Afiliación + Anuncios": 9,
        "Solo Afiliación": 7,
        "Solo Anuncios": 6,
        "Difícil Monetizar": 3
    }
    
    score = base_scores.get(tipo_monetizacion, 3)
    
    # Bonus por porcentaje de videos monetizables
    bonus_afiliacion = min(2, analisis_titulos['porcentaje_afiliacion'] / 25)  # Máximo 2 puntos
    bonus_anuncios = min(1, analisis_titulos['porcentaje_anuncios'] / 20)  # Máximo 1 punto
    
    final_score = min(10, score + bonus_afiliacion + bonus_anuncios)
    return round(final_score, 1)


def calcular_potencial_total_refinado(avg_views, monetizacion, automatizable, videos_monetizables_pct):
    """
    Calcula el potencial total del nicho (versión refinada 0-100)
    Nueva distribución de pesos con monetización como modificador:
    - Views promedio: 30% (0-30 puntos)
    - Tipo monetización: 35% (0-35 puntos) - reducido pero aún importante
    - Automatización: 25% (0-25 puntos)
    - % videos monetizables: 10% (0-10 puntos) + modificadores
    """
    
    # 1. VIEWS PROMEDIO (30% = 30 puntos máximo)
    if avg_views >= 1000000:
        views_score = 30
    elif avg_views >= 500000:
        views_score = 26
    elif avg_views >= 100000:
        views_score = 22
    elif avg_views >= 50000:
        views_score = 18
    elif avg_views >= 10000:
        views_score = 12
    elif avg_views >= 1000:
        views_score = 8
    else:
        views_score = 3
    
    # 2. TIPO DE MONETIZACIÓN (35% = 35 puntos máximo) - más tolerante
    monetizacion_scores = {
        "Afiliación + Anuncios": 35,
        "Solo Anuncios": 28,
        "Solo Afiliación": 24,
        "Difícil Monetizar": 15  # Aumentado de 5 a 15 para ser menos penalizante
    }
    monetizacion_score = monetizacion_scores.get(monetizacion, 15)
    
    # 3. AUTOMATIZACIÓN (25% = 25 puntos máximo)
    automatizacion_score = 25 if automatizable else 8
    
    # 4. % VIDEOS MONETIZABLES con sistema de modificadores relajado
    base_monetizables = 5  # Puntuación base
    
    if videos_monetizables_pct < 10:
        # Penalizar pero no eliminar (-10 puntos)
        monetizables_modifier = -10
    elif 10 <= videos_monetizables_pct <= 30:
        # Neutro (0 modificador)
        monetizables_modifier = 0
    else:
        # Bonificar (+10 puntos)
        monetizables_modifier = 10
    
    monetizables_score = max(0, base_monetizables + monetizables_modifier)
    
    total = views_score + monetizacion_score + automatizacion_score + monetizables_score
    return min(100, max(0, total))


def exportar_resultados_completos_csv(results, descartados_list, filename=None, out_dir=None, region=None):
    """
    Exporta todos los resultados (aprobados y descartados) en un solo CSV
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if out_dir:
            region_seg = (region or 'unknown').lower()
            out_folder = Path(out_dir) / region_seg / timestamp
            out_folder.mkdir(parents=True, exist_ok=True)
            filename = str(out_folder / "resultados.csv")
        else:
            filename = f"youtube_analisis_completo_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Fieldnames completos para ambos tipos de registros
        fieldnames = [
            'keyword', 'status', 'avg_views', 'median_views', 'pct75_views', 'max_views', 'video_count', 
            'monetizacion', 'automatizable', 'automatizable_count', 
            'score_refinado', 'riesgo_saturacion', 'porcentaje_monetizables',
            'decision', 'reason', 'motivo_descarte'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Escribir comentario para nichos aprobados
        csvfile.write("# NICHOS APROBADOS\n")
        
        # Escribir nichos aprobados
        for result in results:
            row = {
                'keyword': result['keyword'],
                'status': 'APROBADO',
                'avg_views': int(result.get('avg_views', 0)),
                'median_views': int(result.get('median_views', 0)),
                'pct75_views': int(result.get('pct75_views', 0)),
                'max_views': result.get('max_views', ''),
                'video_count': result.get('video_count', ''),
                'monetizacion': result['monetizacion'],
                'automatizable': result['automatizable'],
                'automatizable_count': result['automatizable_count'],
                'score_refinado': result['potencial_total_refinado'],
                'riesgo_saturacion': result['riesgo_saturacion'],
                'porcentaje_monetizables': round(result['analisis_titulos']['porcentaje_monetizables'], 1),
                'decision': result.get('decision', ''),
                'reason': result.get('reason', ''),
                'motivo_descarte': ''
            }
            writer.writerow(row)
        
        # Escribir separador para nichos descartados
        if descartados_list:
            csvfile.write("\n# NICHOS DESCARTADOS\n")
            
            # Escribir nichos descartados
            for descartado in descartados_list:
                row = {
                    'keyword': descartado['keyword'],
                    'status': 'DESCARTADO',
                    'avg_views': descartado.get('avg_views', ''),
                    'median_views': descartado.get('median_views', ''),
                    'pct75_views': descartado.get('pct75_views', ''),
                    'max_views': '',
                    'video_count': '',
                    'monetizacion': descartado.get('tipo_monetizacion', ''),
                    'automatizable': '',
                    'automatizable_count': '',
                    'score_refinado': descartado.get('score_refinado', ''),
                    'riesgo_saturacion': '',
                    'porcentaje_monetizables': '',
                    'decision': descartado.get('decision', ''),
                    'reason': descartado.get('reason', ''),
                    'motivo_descarte': descartado['motivo_descarte']
                }
                writer.writerow(row)
    
    print(f"📄 Análisis completo exportado a: {filename}")
    return filename


def exportar_descartados_csv(descartados, filename=None, out_dir=None, region=None):
    """
    Exporta los nichos descartados a un archivo CSV separado
    """
    if not descartados:
        return None
        
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if out_dir:
            region_seg = (region or 'unknown').lower()
            out_folder = Path(out_dir) / region_seg / timestamp
            out_folder.mkdir(parents=True, exist_ok=True)
            filename = str(out_folder / "descartados.csv")
        else:
            filename = f"youtube_descartados_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['keyword', 'motivo_descarte', 'avg_views', 'tipo_monetizacion', 'score_refinado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for descartado in descartados:
            writer.writerow(descartado)
    
    print(f"📄 Nichos descartados exportados a: {filename}")
    return filename


def search_videos(query, max_results=10, region_code=None, relevance_language=None):
    """
    Busca videos en YouTube por palabra clave
    """
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # Buscar videos
    search_params = dict(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results,
        order="relevance"
    )
    if region_code:
        search_params['regionCode'] = region_code
    if relevance_language:
        search_params['relevanceLanguage'] = relevance_language

    search_request = youtube.search().list(**search_params)

    # Ejecutar con reintentos
    try:
        search_response = execute_with_retries(lambda: search_request.execute())
    except Exception as e:
        print(f"Error de API de YouTube al buscar: {e}")
        return []

    # Obtener IDs de videos para estadísticas
    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

    if not video_ids:
        return []

    # Obtener estadísticas de los videos
    stats_request = youtube.videos().list(
        part="statistics,contentDetails",
        id=",".join(video_ids)
    )

    try:
        stats_response = execute_with_retries(lambda: stats_request.execute())
    except Exception as e:
        print(f"Error de API de YouTube al obtener stats: {e}")
        return []

    # Combinar datos
    results = []
    global api_units_used
    # Cada llamada a search().list cuesta 100 unidades
    api_units_used += 100
    # Cada llamada a videos().list cuesta 1 unidad por video consultado
    api_units_used += len(video_ids)
    for i, item in enumerate(search_response.get('items', [])):
        video_id = item.get('id', {}).get('videoId', '')
        snippet = item.get('snippet', {})
        stats_item = stats_response.get('items', [])[i] if i < len(stats_response.get('items', [])) else {}
        statistics = stats_item.get('statistics', {})
        content_details = stats_item.get('contentDetails', {})
        video_data = {
            'video_id': video_id,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'channelTitle': snippet.get('channelTitle', ''),
            'publishedAt': snippet.get('publishedAt', ''),
            'viewCount': int(statistics.get('viewCount', 0)),
            'likeCount': int(statistics.get('likeCount', 0)),
            'commentCount': int(statistics.get('commentCount', 0)),
            'duration': content_details.get('duration', '')
        }
        results.append(video_data)

    return results


def execute_with_retries(callable_func, max_retries=5, initial_backoff=1.0, backoff_factor=2.0):
    """Ejecuta una función que realiza una llamada de red y reintenta en errores transitorios.

    callable_func: función sin argumentos que realiza la llamada (p. ej. lambda: request.execute())
    max_retries: número máximo de intentos
    initial_backoff: segundos iniciales de espera
    backoff_factor: multiplicador exponencial
    """
    backoff = float(initial_backoff)
    for attempt in range(1, max_retries + 1):
        try:
            return callable_func()
        except HttpError as he:
            # Intentar extraer el código de estado
            status = None
            try:
                status = int(he.resp.status)
            except Exception:
                pass

            # Reintentar para 403, 429 y 5xx
            if status in (403, 429) or (status and 500 <= status < 600):
                if attempt == max_retries:
                    raise
                sleep_time = backoff + random.uniform(0, 0.5 * backoff)
                print(f"⚠️ HttpError {status} — reintento {attempt}/{max_retries} en {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                backoff *= backoff_factor
                continue
            # Otros HttpError: re-lanzar
            raise
        except Exception as e:
            # Para errores genéricos (p. ej. timeouts) también reintentamos
            if attempt == max_retries:
                raise
            sleep_time = backoff + random.uniform(0, 0.5 * backoff)
            print(f"⚠️ Error de red ({e}) — reintento {attempt}/{max_retries} en {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            backoff *= backoff_factor
    # Si llega aquí, todos los reintentos fallaron
    raise RuntimeError("Máximo de reintentos alcanzado")


def compute_median_and_percentile(values, percentile=75):
    """Devuelve la mediana y el percentil indicado (ej. 75) de una lista de valores.

    Usa interpolación lineal cuando sea necesario.
    """
    if not values:
        return 0, 0
    vals = sorted(values)
    median = statistics.median(vals)

    # Cálculo de percentil con interpolación similar a numpy.percentile(method='linear')
    k = (len(vals) - 1) * (percentile / 100.0)
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        pct_val = vals[int(k)]
    else:
        d0 = vals[f] * (c - k)
        d1 = vals[c] * (k - f)
        pct_val = d0 + d1

    return median, pct_val


def analyze_niche_with_tracking(keyword, descartados_list, region_code=None, relevance_language=None, median_min=None, p75_min=None):
    """
    Analiza un nicho específico en YouTube con métricas siempre visibles y decisión suave
    """
    print(f"🔍 Analizando nicho: {keyword}")
    
    videos = search_videos(keyword, max_results=20, region_code=region_code, relevance_language=relevance_language)
    
    if not videos:
        print("❌ No se encontraron videos")
        result = {
            'keyword': keyword,
            'region': region_code or 'N/A',
            'results_count': 0,
            'avg_views': 0,
            'median_views': 0,
            'pct75_views': 0,
            'max_views': 0,
            'decision': 'DESCARTAR',
            'reason': 'Sin videos encontrados',
            'score_base': 0.0,
            'score_refinado': 0.0,
            'monetizacion': 'N/A',
            'automatizable': False,
            'automatizable_count': 0,
            'monetizable_ratio_pct': 0.0,
            'riesgo_saturacion': 'N/A'
        }
        descartados_list.append(result.copy())
        return result
    
    # TODO: Mostrar siempre métricas y luego la decisión (sin early return por descarte)
    count = len(videos)
    total_views = sum(v['viewCount'] for v in videos)
    avg_views = total_views / count
    views_list = [v['viewCount'] for v in videos]
    median_views, pct75_views = compute_median_and_percentile(views_list, 75)
    max_views = max(v['viewCount'] for v in videos)
    
    # Usar umbrales pasados o defaults globales
    actual_median_min = median_min if median_min is not None else MEDIAN_MIN
    actual_p75_min = p75_min if p75_min is not None else PCT75_MIN
    
    # imprimir bloque con métricas SIEMPRE
    print(f"📊 Resultados para '{keyword}':")
    print(f"   Videos encontrados: {count}")
    print(f"   Views promedio: {avg_views:,.0f}")
    print(f"   Mediana views: {median_views:,.0f}")
    print(f"   Percentil 75 views: {pct75_views:,.0f}")
    print(f"   Views máximas: {max_views:,.0f}")
    
    # decisión suave
    decision, reason, base_score = decide_niche_soft(median_views, pct75_views, actual_median_min, actual_p75_min)
    
    # Análisis adicional para score refinado
    monetizacion_keyword = clasificar_monetizacion(keyword)
    sorted_videos = sorted(videos, key=lambda x: x['viewCount'], reverse=True)[:5]
    analisis_titulos = analizar_titulos_monetizacion(videos)
    
    # Automatización
    automatizable_count = sum([is_automatizable(v['title']) for v in sorted_videos])
    automatizable = automatizable_count >= 3
    
    # monetización/automatización ajustan SOLO el score, no la 'decision' base
    score_refinado = base_score
    
    # Aplicar modificadores de monetización
    if monetizacion_keyword == "Afiliación + Anuncios":
        score_refinado += 10
    elif monetizacion_keyword == "Solo Anuncios":
        score_refinado += 5
    elif monetizacion_keyword == "Solo Afiliación":
        score_refinado += 3
    else:  # "Difícil Monetizar"
        score_refinado -= 5
    
    # Modificador por automatización
    if automatizable:
        score_refinado += 5
    else:
        score_refinado -= 2
    
    # TODO: Relajar el umbral mínimo de "videos monetizables":
    monetizable_ratio_pct = analisis_titulos['porcentaje_monetizables']
    if monetizable_ratio_pct < 10:
        score_refinado -= 10  # penalizar score (-10), pero NO descartar
    elif 10 <= monetizable_ratio_pct <= 30:
        pass  # neutro
    else:
        score_refinado += 10  # bonificar score (+10)
    
    # Clamp score refinado
    score_refinado = max(0.0, min(100.0, score_refinado))
    
    # Semáforo de saturación (riesgo visual)
    saturacion_ratio = avg_views / max_views
    if saturacion_ratio >= 0.8:
        riesgo_saturacion_visual = "🟢 Bajo"
    elif 0.4 <= saturacion_ratio < 0.8:
        riesgo_saturacion_visual = "🟡 Medio"
    else:
        riesgo_saturacion_visual = "🔴 Alto"
    
    print(f"   💰 Monetización: {monetizacion_keyword}")
    print(f"   🤖 Automatizable: {'✅ Sí' if automatizable else '❌ No'} ({automatizable_count}/5 videos)")
    print(f"   ⚠️ Riesgo saturación: {riesgo_saturacion_visual}")
    print(f"   📈 Videos monetizables: {monetizable_ratio_pct:.1f}%")
    print(f"   🎯 Decisión: {decision} | {reason}")
    print(f"   🧮 Score base: {base_score:.1f} | Score refinado: {score_refinado:.1f}")
    
    # Mostrar top 5 videos con clasificación
    print(f"\n🏆 Top 5 videos más populares:")
    for i, video in enumerate(sorted_videos, 1):
        auto_icon = "🤖" if is_automatizable(video['title']) else "👤"
        print(f"   {i}. {auto_icon} {video['title'][:60]}... - {video['viewCount']:,} views")
    
    print("----------------------------------------------------------------------")

    # TODO: Incluir métricas aun si 'DESCARTAR'
    result = {
        "keyword": keyword,
        "region": region_code or 'N/A',
        "results_count": count,
        "avg_views": int(avg_views),
        "median_views": int(median_views),
        "pct75_views": int(pct75_views),
        "max_views": int(max_views),
        "decision": decision,
        "reason": reason,
        "score_base": base_score,
        "score_refinado": score_refinado,
        "monetizacion": monetizacion_keyword,
        "automatizable": automatizable,
        "automatizable_count": automatizable_count,
        "monetizable_ratio_pct": monetizable_ratio_pct,
        "riesgo_saturacion": riesgo_saturacion_visual,
        # Legacy fields for compatibility
        'video_count': count,
        'total_views': total_views,
        'top_videos': sorted_videos,
        'analisis_titulos': analisis_titulos,
        'score_monetizacion': calcular_score_monetizacion(monetizacion_keyword, analisis_titulos),
        'potencial_total_refinado': score_refinado
    }
    
    # Agregar a lista de descartados si es necesario
    if decision == 'DESCARTAR':
        descartados_list.append(result.copy())
    
    return result


def analyze_niche(keyword, region_code=None, relevance_language=None):
    """
    Analiza un nicho específico en YouTube con filtros de calidad
    """
    print(f"🔍 Analizando nicho: {keyword}")
    
    videos = search_videos(keyword, max_results=20, region_code=region_code, relevance_language=relevance_language)
    
    if not videos:
        print("❌ No se encontraron videos")
    return None
    
    # Calcular métricas básicas
    total_views = sum(v['viewCount'] for v in videos)
    avg_views = total_views / len(videos)
    # Mediana y percentil 75
    views_list = [v['viewCount'] for v in videos]
    median_views, pct75_views = compute_median_and_percentile(views_list, 75)
    max_views = max(v['viewCount'] for v in videos)
    
    # ✅ 1. Filtro por views promedio bajos
    # Ignorar nichos con menos de 10.000 views promedio
    if avg_views < 10000:
        print(f"⚠️ Nicho '{keyword}' descartado: views promedio demasiado bajos ({avg_views:,.0f})")
    return None
    
    # Ordenar videos por popularidad
    sorted_videos = sorted(videos, key=lambda x: x['viewCount'], reverse=True)[:5]
    
    # 🧩 CLASIFICACIONES REFINADAS
    monetizacion_keyword = clasificar_monetizacion(keyword)
    
    analisis_titulos = analizar_titulos_monetizacion(videos)
    
    # Automatización
    automatizable_count = sum([is_automatizable(v['title']) for v in sorted_videos])
    automatizable = automatizable_count >= 3  # Al menos 3 de 5 videos automatizables
    
    # Score refinado con nueva fórmula (la monetización ahora es solo un modificador)
    potencial_total_refinado = calcular_potencial_total_refinado(
        avg_views, 
        monetizacion_keyword, 
        automatizable,
        analisis_titulos['porcentaje_monetizables']
    )
    
    # ✅ 2. Filtro por score refinado mínimo
    # Filtrar nichos con score bajo
    if potencial_total_refinado < 50:
        print(f"❌ Nicho '{keyword}' eliminado: score demasiado bajo ({potencial_total_refinado})")
    return None
    
    # ✅ 4. Semáforo de saturación (riesgo visual)
    # Calcular riesgo de saturación con semáforo
    saturacion_ratio = avg_views / max_views
    if saturacion_ratio >= 0.8:
        riesgo_saturacion_visual = "🟢 Bajo"
    elif 0.4 <= saturacion_ratio < 0.8:
        riesgo_saturacion_visual = "🟡 Medio"
    else:
        riesgo_saturacion_visual = "🔴 Alto"
    
    # Mostrar resultados
    print(f"�📊 Resultados para '{keyword}':")
    print(f"   Videos encontrados: {len(videos)}")
    print(f"   Views promedio: {avg_views:,.0f}")
    print(f"   Mediana views: {median_views:,.0f}")
    print(f"   Percentil 75 views: {pct75_views:,.0f}")
    print(f"   Views máximas: {max_views:,.0f}")
    print(f"   💰 Monetización: {monetizacion_keyword}")
    print(f"   🤖 Automatizable: {'✅ Sí' if automatizable else '❌ No'} ({automatizable_count}/5 videos)")
    print(f"   ⚠️ Riesgo saturación: {riesgo_saturacion_visual}")
    print(f"   📈 Videos monetizables: {analisis_titulos['porcentaje_monetizables']:.1f}%")
    print(f"   🎯 Potencial REFINADO: {potencial_total_refinado}/100")
    
    # Mostrar top 5 videos con clasificación
    print(f"\n🏆 Top 5 videos más populares:")
    for i, video in enumerate(sorted_videos, 1):
        auto_icon = "🤖" if is_automatizable(video['title']) else "👤"
    print(f"   {i}. {auto_icon} {video['title'][:60]}... - {video['viewCount']:,} views")
    
    # --- Decidir usando decide_niche ---
    decision, reason = decide_niche(median_views, pct75_views)

    return {
        'keyword': keyword,
        'region': region_code or 'N/A',
        'video_count': len(videos),
        'avg_views': avg_views,
        'median_views': median_views,
        'pct75_views': pct75_views,
        'max_views': max_views,
        'total_views': total_views,
        'top_videos': sorted_videos,
        'monetizacion': monetizacion_keyword,
        'automatizable': automatizable,
        'automatizable_count': automatizable_count,
        'riesgo_saturacion': riesgo_saturacion_visual,
        'analisis_titulos': analisis_titulos,
        'score_monetizacion': calcular_score_monetizacion(monetizacion_keyword, analisis_titulos),
        'potencial_total_refinado': potencial_total_refinado,
        'decision': decision,
        'reason': reason
    }


def get_keywords_manual():
    """Pide al usuario que introduzca hasta 10 keywords manualmente."""
    keywords = []
    print("💡 Introduce las keywords que quieres analizar (máximo 10):")
    for i in range(10):
        keyword = input(f"Keyword {i+1}: ").strip()
        if keyword:
            keywords.append(keyword)
        else:
            break
    return keywords

def get_keywords_from_file():
    """Lee las keywords desde un archivo llamado keywords_to_check.txt."""
    try:
        with open("keywords_to_check.txt", "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
        print(f"📄 Keywords cargadas desde archivo: {len(keywords)} encontradas.")
        return keywords[:10]  # Limitar a 10 keywords
    except FileNotFoundError:
        print("❌ El archivo keywords_to_check.txt no existe. Por favor, créalo y añade una keyword por línea.")
        return []

def get_keywords_from_pytrends(pn='spain', geo='ES', hl='es-ES'):
    """Obtiene keywords populares usando PyTrends. Parámetros pasados desde CLI.
    pn: parámetro para trending_searches (p. ej. 'spain' o 'united_states')
    geo: código geo para payload (p. ej. 'ES' o 'US')
    hl: idioma/locale para PyTrends (p. ej. 'es-ES')
    """
    try:
        from pytrends.request import TrendReq
    except Exception as e:
        print(f"❌ pytrends no está instalado o no se puede importar: {e}")
        return []

    pytrends = TrendReq(hl=hl, tz=360)

    try:
        print("🔥 Obteniendo tendencias de Google Trends...")
        # Build payload with a sensible timeframe for related queries
        try:
            pytrends.build_payload(kw_list=[""], geo=geo, timeframe="today 3-m", hl=hl)
        except Exception:
            # Si falla con lista vacía, no detener -- construiremos después
            pass

        # Intentar trending_searches con el pn pedido; si falla, hacer fallback
        try:
            print(f"🌍 Intentando trending_searches(pn={pn})")
            trending_searches = pytrends.trending_searches(pn=pn)
        except Exception as e:
            print(f"⚠️ pn='{pn}' no válido o error: {e}. Haciendo fallback a 'spain'.")
            try:
                trending_searches = pytrends.trending_searches(pn='spain')
            except Exception as e2:
                print(f"⚠️ Fallback a 'spain' falló: {e2}. Intentando 'united_states'.")
                try:
                    trending_searches = pytrends.trending_searches(pn='united_states')
                except Exception as e3:
                    print(f"❌ No se pudo obtener trending_searches: {e3}")
                    return []

        keywords = trending_searches.head(10)[0].tolist()
        print(f"📈 Keywords populares detectadas: {keywords}")
        return keywords
    except Exception as e:
        print(f"❌ Error obteniendo tendencias (final): {e}")
        return []


def export_results_dataframe(results, descartados_list, args):
    """Exporta resultados usando pandas. Crea carpeta out/<ts>/ y guarda CSV y opcionalmente parquet y archivos separados.
    """
    if pd is None:
        raise RuntimeError('pandas no está instalado en el entorno. Instala pandas y pyarrow para exportar a parquet.')

    # Combinar resultados y descartados en un DataFrame uniforme
    all_rows = []
    for r in results:
        row = r.copy()
        # Asegurar campo region
        row.setdefault('region', getattr(args, 'region_code', 'N/A'))
        all_rows.append(row)
    for d in descartados_list:
        # Normalizar claves de descartados para que coincidan
        row = {
            'keyword': d.get('keyword'),
            'video_count': d.get('video_count', ''),
            'avg_views': d.get('avg_views', ''),
            'median_views': d.get('median_views', ''),
            'pct75_views': d.get('pct75_views', ''),
            'max_views': d.get('max_views', ''),
            'total_views': d.get('total_views', ''),
            'monetizacion': d.get('tipo_monetizacion', ''),
            'automatizable': d.get('automatizable', ''),
            'automatizable_count': d.get('automatizable_count', ''),
            'potencial_total_refinado': d.get('score_refinado', d.get('potencial_total_refinado', '')),
            'decision': d.get('decision', 'DESCARTADO'),
            'reason': d.get('reason', d.get('motivo_descarte', ''))
        }
        all_rows.append(row)

    df = pd.DataFrame(all_rows)

    # Normalizar cadenas vacías a None para que pyarrow no falle
    df = df.replace({'': None})

    # Asegurar columnas necesarias
    for col in ['decision', 'pct75_views', 'median_views']:
        if col not in df.columns:
            df[col] = None

    # Coercionar columnas numéricas cuando existan
    numeric_cols = ['video_count', 'avg_views', 'median_views', 'pct75_views', 'max_views', 'total_views', 'automatizable_count', 'potencial_total_refinado']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Orden según decisión y percentiles
    df['decision'] = pd.Categorical(df['decision'], ["RECOMENDADO", "EVALUAR", "DESCARTAR"], ordered=True)
    df = df.sort_values(['decision', 'pct75_views', 'median_views'], ascending=[True, False, False])

    # Crear carpeta de salida: out/{region-lower}/{ts}
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    region_seg = (getattr(args, 'region_code', 'unknown') or 'unknown').lower()
    out_path = Path(args.out_dir) / region_seg / ts
    out_path.mkdir(parents=True, exist_ok=True)

    # CSV base
    csv_path = out_path / 'resultados.csv'
    df.to_csv(csv_path, index=False)

    # Parquet opcional
    if getattr(args, 'parquet', False):
        parquet_path = out_path / 'resultados.parquet'
        df.to_parquet(parquet_path, index=False)

    # Archivos separados opcional
    if getattr(args, 'separate_files', False):
        for dec in ["RECOMENDADO", "EVALUAR", "DESCARTAR"]:
            dfd = df[df['decision'] == dec]
            if not dfd.empty:
                dfd.to_csv(out_path / f"{dec.lower()}_{ts}.csv", index=False)

    print(f"📁 Resultados exportados en: {out_path}")
    return out_path


def publish_results(out_path: Path, dest_dir: str):
    """Copia los archivos principales desde out_path a dest_dir y genera resultados.md atractivo"""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    # Copiar resultados.csv si existe
    csv_src = out_path / 'resultados.csv'
    parquet_src = out_path / 'resultados.parquet'
    if csv_src.exists():
        shutil.copy2(str(csv_src), str(dest / 'resultados.csv'))

    if parquet_src.exists():
        try:
            shutil.copy2(str(parquet_src), str(dest / 'resultados.parquet'))
        except Exception:
            pass

    # Generar MD atractivo con análisis completo
    md_path = dest / 'resultados.md'
    if csv_src.exists():
        try:
            # Leer el CSV completo para análisis
            import csv
            with open(csv_src, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            # Generar MD atractivo
            generate_attractive_md(md_path, rows, csv_src)

        except Exception as e:
            # Fallback al MD simple si hay error
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('# 📊 Informe YouTube\n\n')
                f.write('❌ Error generando informe detallado\n\n')
                f.write(f'Error: {e}\n\n')
                f.write('Archivo CSV disponible en: ' + str(csv_src) + '\n')

    return dest


def generate_attractive_md(md_path: Path, rows: list, csv_src: Path):
    """Genera un archivo Markdown visualmente atractivo con el análisis completo"""

    with open(md_path, 'w', encoding='utf-8') as f:
        # Encabezado principal con mejor formato
        f.write('# 🎯 Análisis de Nichos YouTube\n\n')
        f.write('> 📅 **Generado:** ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n\n')
        f.write('> 📁 **Archivo origen:** `' + str(csv_src) + '`\n\n')
        f.write('> 🌍 **Región analizada:** ' + (rows[0].get('region', 'N/A') if rows else 'N/A') + '\n\n')

        if not rows:
            f.write('❌ **No se encontraron resultados para analizar**\n\n')
            return

        # Estadísticas generales con mejor formato
        total_nichos = len(rows)
        nichos_recomendados = sum(1 for r in rows if r.get('decision') == 'RECOMENDADO')
        nichos_evaluados = sum(1 for r in rows if r.get('decision') == 'EVALUAR')
        nichos_descartados = sum(1 for r in rows if r.get('decision') == 'DESCARTADO')

        # Calcular promedios
        avg_views_total = sum(float(r.get('avg_views', 0)) for r in rows) / len(rows) if rows else 0
        avg_score_total = sum(float(r.get('potencial_total_refinado', 0)) for r in rows) / len(rows) if rows else 0

        f.write('## 📊 Estadísticas Generales\n\n')
        f.write('| 📈 Métrica | 📊 Valor |\n')
        f.write('|-------------|----------|\n')
        f.write(f'| 🎯 Nichos Analizados | **{total_nichos}** |\n')
        f.write(f'| ✅ Recomendados | **{nichos_recomendados}** |\n')
        f.write(f'| 🤔 Para Evaluar | **{nichos_evaluados}** |\n')
        f.write(f'| ❌ Descartados | **{nichos_descartados}** |\n')
        f.write(f'| 👀 Views Promedio | **{int(avg_views_total):,}** |\n')
        f.write(f'| 🎯 Score Promedio | **{avg_score_total:.1f}/100** |\n')
        f.write('\n')

        # Top oportunidades mejorado
        if rows:
            # Ordenar por score refinado descendente
            sorted_rows = sorted(rows, key=lambda x: float(x.get('potencial_total_refinado', 0)), reverse=True)

            f.write('## 🏆 Top Oportunidades\n\n')

            for i, row in enumerate(sorted_rows[:5], 1):
                score = float(row.get('potencial_total_refinado', 0))
                decision = row.get('decision', '')

                # Icono según decisión
                if decision == 'RECOMENDADO':
                    icon = '🚀'
                elif decision == 'EVALUAR':
                    icon = '⭐'
                else:
                    icon = '✅'

                # Barra de progreso para el score
                filled = int(score / 10)
                empty = 10 - filled
                progress_bar = '█' * filled + '░' * empty

                # Nivel de calidad
                if score >= 80:
                    quality = '🔥 EXCELENTE'
                elif score >= 70:
                    quality = '💎 MUY BUENO'
                elif score >= 60:
                    quality = '✨ BUENO'
                else:
                    quality = '📈 ACEPTABLE'

                f.write(f'### {i}. {icon} {row.get("keyword", "")}\n\n')
                f.write(f'**🏆 Calidad:** {quality}\n\n')
                f.write(f'**📊 Score:** {score:.1f}/100 {progress_bar}\n\n')
                f.write(f'**👀 Views promedio:** {int(float(row.get("avg_views", 0))):,}\n\n')
                f.write(f'**📈 Videos encontrados:** {row.get("video_count", "N/A")}\n\n')
                f.write(f'**💰 Monetización:** {row.get("monetizacion", "")}\n\n')
                f.write(f'**🤖 Automatizable:** {"✅ Sí" if row.get("automatizable") == "True" else "❌ No"}\n\n')
                f.write(f'**⚠️ Riesgo saturación:** {row.get("riesgo_saturacion", "")}\n\n')
                f.write('---\n\n')

        # Análisis detallado por decisión
        f.write('## 📈 Análisis Detallado por Categoría\n\n')

        for decision, title, emoji in [
            ('RECOMENDADO', 'Nichos Recomendados', '🚀'),
            ('EVALUAR', 'Nichos para Evaluar', '⭐'),
            ('DESCARTADO', 'Nichos Descartados', '❌')
        ]:
            decision_rows = [r for r in rows if r.get('decision') == decision]
            if decision_rows:
                # Ordenar por score dentro de cada categoría
                decision_rows.sort(key=lambda x: float(x.get('potencial_total_refinado', 0)), reverse=True)

                f.write(f'### {emoji} {title} ({len(decision_rows)} nichos)\n\n')

                for row in decision_rows:
                    score = float(row.get('potencial_total_refinado', 0))
                    filled = int(score / 10)
                    empty = 10 - filled
                    progress_bar = '█' * filled + '░' * empty

                    f.write(f'#### {row.get("keyword", "")}\n\n')
                    f.write(f'**📊 Score:** {score:.1f}/100 {progress_bar}\n\n')
                    f.write(f'**👀 Views promedio:** {int(float(row.get("avg_views", 0))):,}\n\n')
                    f.write(f'**📈 Videos encontrados:** {row.get("video_count", "N/A")}\n\n')
                    f.write(f'**💰 Monetización:** {row.get("monetizacion", "")}\n\n')
                    f.write(f'**🤖 Automatizable:** {"✅ Sí" if row.get("automatizable") == "True" else "❌ No"}\n\n')
                    f.write(f'**⚠️ Riesgo saturación:** {row.get("riesgo_saturacion", "")}\n\n')
                    f.write('\n')

        # Insights y recomendaciones mejorados
        f.write('## 💡 Insights y Recomendaciones\n\n')

        if nichos_recomendados > 0:
            f.write('### ✅ **Fortalezas Detectadas**\n\n')
            f.write(f'🎯 **{nichos_recomendados} nichos** cumplen todos los criterios de calidad\n\n')
            f.write('📈 Alto potencial de crecimiento y monetización\n\n')
            f.write('🎪 Buena combinación de views y engagement\n\n')

            # Recomendación específica del mejor nicho
            if sorted_rows:
                best_nicho = sorted_rows[0]
                f.write(f'🏆 **Mejor Oportunidad:** `{best_nicho.get("keyword", "")}`\n\n')
                f.write(f'💰 **Monetización:** {best_nicho.get("monetizacion", "")}\n\n')
                f.write(f'🎯 **Score:** {float(best_nicho.get("potencial_total_refinado", 0)):.1f}/100\n\n')

        if nichos_evaluados > 0:
            f.write('### 🤔 **Oportunidades de Mejora**\n\n')
            f.write(f'📊 **{nichos_evaluados} nichos** necesitan evaluación adicional\n\n')
            f.write('🔍 Revisar estrategia de contenido y optimización SEO\n\n')
            f.write('💡 Considerar nichos relacionados con mejor performance\n\n')

        if nichos_descartados > 0:
            f.write('### ❌ **Lecciones Aprendidas**\n\n')
            f.write(f'📉 **{nichos_descartados} nichos** no cumplen criterios mínimos\n\n')
            f.write('🎯 Enfocarse en keywords con mayor volumen de búsqueda\n\n')
            f.write('🔄 Probar variaciones de las keywords descartadas\n\n')

        # Consejos finales
        f.write('## 🎯 Consejos para el Éxito\n\n')
        f.write('### 📝 Estrategia de Contenido\n')
        f.write('- 🎬 Crear contenido de alta calidad y valor\n')
        f.write('- 📱 Optimizar para móvil y SEO de YouTube\n')
        f.write('- 📊 Analizar métricas regularmente\n\n')

        f.write('### 💰 Estrategia de Monetización\n')
        f.write('- 💳 Considerar programas de afiliación\n')
        f.write('- � Explorar publicidad de YouTube\n')
        f.write('- 🤝 Colaboraciones con marcas\n\n')

        f.write('### 📈 Crecimiento\n')
        f.write('- 📊 Usar analytics para entender la audiencia\n')
        f.write('- 📱 Promocionar en redes sociales\n')
        f.write('- 🎯 Crear series y contenido consistente\n\n')

        # Footer mejorado
        f.write('---\n\n')
        f.write('📄 **Archivos disponibles:**\n\n')
        f.write('- 📊 `resultados.csv` - Datos completos en formato CSV\n')
        f.write('- 📋 `resultados.parquet` - Datos optimizados para análisis\n\n')
        f.write('🤖 **Análisis generado automáticamente por YouTube Analyzer**\n')
        f.write('📅 **Fecha de generación:** ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')

def main():
    """Función principal del script."""
    # Allow CLI to override module-level thresholds
    global MEDIAN_VIEWS_THRESHOLD, P75_VIEWS_THRESHOLD

    parser = argparse.ArgumentParser(description='Analizador de nichos YouTube')
    parser.add_argument('--region-code', choices=['ES', 'US'], default='ES', help='Código de región para YouTube (ES/US)')
    parser.add_argument('--lang', choices=['es', 'en'], default='es', help='Idioma de relevancia para YouTube (es/en)')
    parser.add_argument('--pn', choices=['spain', 'united_states'], default=None, help='pn para PyTrends (spain/united_states)')
    parser.add_argument('--geo', choices=['ES', 'US'], default=None, help='geo para PyTrends payload (ES/US)')
    parser.add_argument('--hl', default=None, help='hl para PyTrends (ej. es-ES, en-US)')
    parser.add_argument('--median-min', type=int, default=None, help='Umbral mediana (si no se pasa, se usan defaults por región)')
    parser.add_argument('--pct75-min', type=int, default=None, help='Umbral P75 (si no se pasa, se usan defaults por región)')
    parser.add_argument('--out-dir', default='out', help='Directorio de salida')
    parser.add_argument('--separate-files', action='store_true', help='Generar CSV separados por decisión')
    parser.add_argument('--parquet', action='store_true', help='Generar archivo parquet adicional')
    parser.add_argument('--interactive', action='store_true', help='Usar menú interactivo para seleccionar keywords')
    parser.add_argument('--publish-desktop', action='store_true', help='Copiar resultados y generar MD en el Escritorio (Script Youtube)')
    parser.add_argument('--publish-dir', default=None, help='Copiar resultados y generar MD en la carpeta indicada')
    args = parser.parse_args()

    # TODO: Ajustar defaults por región:
    # ES: MEDIAN_MIN=5000, P75_MIN=20000 (igual)
    # US: MEDIAN_MIN=10000, P75_MIN=30000  # antes 40000
    MEDIAN_DEFAULTS = {"ES": 5000, "US": 10000}
    P75_DEFAULTS = {"ES": 20000, "US": 30000}
    
    region_defaults = {
        'ES': {'median': MEDIAN_DEFAULTS["ES"], 'pct75': P75_DEFAULTS["ES"]},
        'US': {'median': MEDIAN_DEFAULTS["US"], 'pct75': P75_DEFAULTS["US"]}
    }

    # Validar que el usuario no haya pasado --region-code más de una vez
    region_flags = sum(1 for a in sys.argv if a.startswith('--region-code'))
    if region_flags > 1:
        print("❌ Se ha pasado más de una --region-code. Solo se permite una región por ejecución.")
        sys.exit(2)

    selected_region = args.region_code

    # Forzar defaults de pn/geo/hl según región solo si el usuario no los pasó
    region_pytrends_defaults = {
        'ES': {'pn': 'spain', 'geo': 'ES', 'hl': 'es-ES'},
        'US': {'pn': 'united_states', 'geo': 'US', 'hl': 'en-US'}
    }

    py_defaults = region_pytrends_defaults.get(selected_region, {})
    # Si el usuario no pasó pn/geo/hl, usar los defaults de la región
    args.pn = args.pn if args.pn is not None else py_defaults.get('pn')
    args.geo = args.geo if args.geo is not None else py_defaults.get('geo')
    args.hl = args.hl if args.hl is not None else py_defaults.get('hl')

    if args.median_min is not None:
        MEDIAN_VIEWS_THRESHOLD = int(args.median_min)
    else:
        MEDIAN_VIEWS_THRESHOLD = region_defaults.get(selected_region, {}).get('median', MEDIAN_VIEWS_THRESHOLD)

    if args.pct75_min is not None:
        P75_VIEWS_THRESHOLD = int(args.pct75_min)
    else:
        P75_VIEWS_THRESHOLD = region_defaults.get(selected_region, {}).get('pct75', P75_VIEWS_THRESHOLD)

    # Mantener alias antiguos para compatibilidad
    globals()['MEDIAN_MIN'] = MEDIAN_VIEWS_THRESHOLD
    globals()['PCT75_MIN'] = P75_VIEWS_THRESHOLD

    # Log rápido de configuración
    print(f"REGION={args.region_code} | LANG={args.lang} | PN={args.pn} | GEO={args.geo} | HL={args.hl} | MEDIAN_MIN={MEDIAN_VIEWS_THRESHOLD} | P75_MIN={P75_VIEWS_THRESHOLD}")

    if args.interactive:
        print("=== ¿Cómo quieres obtener las keywords? ===")
        print("1. Introducir a mano (modo testing)")
        print("2. Leer desde archivo (keywords_to_check.txt)")
        print("3. Detectar automáticamente con Google Trends")

        option = input("Elige una opción (1/2/3): ").strip()

        if option == "1":
            keywords = get_keywords_manual()
        elif option == "2":
            keywords = get_keywords_from_file()
        elif option == "3":
            keywords = get_keywords_from_pytrends(pn=args.pn, geo=args.geo, hl=args.hl)
        else:
            print("❌ Opción no válida. Saliendo...")
            return
    else:
        # No interactivo: leer archivo por defecto
        keywords = get_keywords_from_file()

    if not keywords:
        print("❌ No se encontraron keywords. Saliendo...")
        return

    print(f"\n🔍 Analizando {len(keywords)} keyword(s)...\n")

    results = []
    descartados_list = []  # Lista para registrar nichos descartados
    all_results = []  # Lista para todos los resultados (incluye descartados)

    for keyword in keywords:
        # Pasar región y lenguaje de relevancia a las llamadas de búsqueda de YouTube
        relevance_lang = 'es' if args.lang == 'es' else 'en'
        result = analyze_niche_with_tracking(
            keyword, 
            descartados_list, 
            region_code=args.region_code, 
            relevance_language=relevance_lang,
            median_min=MEDIAN_VIEWS_THRESHOLD,
            p75_min=P75_VIEWS_THRESHOLD
        )
        
        # TODO: Exportar SIEMPRE filas completas (incl. descartados) con métricas
        all_results.append(result)
        
        # Solo añadir a 'results' si no fue descartado (para compatibilidad con código existente)
        if result and result.get('decision') not in ['DESCARTADO', 'DESCARTAR']:
            results.append(result)

    # Exportar todos los resultados en un solo archivo CSV (y opcional Parquet / separados)
    out_path = None
    if all_results:
        print(f"\n📋 Generando informe completo...")
        print(f"   ✅ Nichos aprobados: {len(results)}")
        print(f"   ❌ Nichos descartados: {len(descartados_list)}")
        print(f"   📊 Total analizados: {len(all_results)}")
        # Usar pandas si está disponible para exportaciones avanzadas
        try:
            out_path = export_results_dataframe(all_results, [], args)  # Pasar todos los resultados, descartados lista vacía
        except Exception as e:
            print(f"⚠️ Error exportando con pandas: {e}. Usando CSV simple.")
            try:
                filename = exportar_resultados_completos_csv(results, descartados_list, out_dir=args.out_dir, region=args.region_code)
            except Exception as e2:
                print(f"❌ Error exportando CSV completo: {e2}")
                filename = None
            try:
                exportar_descartados_csv(descartados_list, out_dir=args.out_dir, region=args.region_code)
            except Exception:
                pass
            if filename:
                out_path = Path(filename).parent

    # Resumen final con ranking de solo nichos viables
    if results:
        print(f"\n📈 NICHOS VIABLES ENCONTRADOS - {len(results)} de {len(keywords)}:")
        print("=" * 70)
        
        # Normalizar y coercionar campos numéricos importantes
        for r in results:
            try:
                r['potencial_total_refinado'] = float(r.get('potencial_total_refinado') or 0)
            except Exception:
                r['potencial_total_refinado'] = 0.0
            try:
                r['pct75_views'] = float(r.get('pct75_views') or 0)
            except Exception:
                r['pct75_views'] = 0.0
            try:
                r['median_views'] = float(r.get('median_views') or 0)
            except Exception:
                r['median_views'] = 0.0

        # Ordenar por decision (RECOMENDADO > EVALUAR > DESCARTADO) y luego por pct75_views
        decision_priority = {'RECOMENDADO': 2, 'EVALUAR': 1, 'DESCARTADO': 0}
        results_sorted = sorted(
            results,
            key=lambda x: (decision_priority.get(x.get('decision', ''), 0), x.get('pct75_views', 0)),
            reverse=True,
        )
        
        for i, result in enumerate(results_sorted, 1):
            status_icon = "🚀" if result['potencial_total_refinado'] >= 80 else "⭐" if result['potencial_total_refinado'] >= 60 else "✅"
            auto_icon = "🤖" if result['automatizable'] else "👤"
            
            print(f"{i}. {status_icon} {result['keyword']}")
            print(f"   💰 {result['monetizacion']} | {auto_icon} Auto: {result['automatizable_count']}/5")
            print(f"   📊 Score refinado: {result['potencial_total_refinado']}/100")
            print(f"   ⚠️ Saturación: {result['riesgo_saturacion']} | 📈 Monetizables: {result['analisis_titulos']['porcentaje_monetizables']:.1f}%")
            print(f"   👀 {result['avg_views']:,.0f} views promedio")
            print()
        
        # Estadísticas finales
        automatizables = sum(1 for r in results if r['automatizable'])
        alta_calidad = sum(1 for r in results if r['potencial_total_refinado'] >= 70)
        
        print(f"📊 ESTADÍSTICAS DE CALIDAD:")
        print(f"   ✅ Nichos aprobados: {len(results)}/{len(keywords)} ({len(results)/len(keywords)*100:.1f}%)")
        print(f"   ❌ Nichos descartados: {len(descartados_list)}")
        print(f"   🤖 Automatizables: {automatizables}/{len(results)} ({automatizables/len(results)*100:.1f}%)")
        print(f"   🚀 Alta calidad (>70): {alta_calidad}/{len(results)} ({alta_calidad/len(results)*100:.1f}%)")
        
        # Recomendación final
        top_nicho = results_sorted[0]
        print(f"\n🏆 MEJOR OPORTUNIDAD: '{top_nicho['keyword']}'")
        print(f"   💰 Monetización: {top_nicho['monetizacion']}")
        print(f"   🤖 Automatización: {'✅ Sí' if top_nicho['automatizable'] else '❌ Requiere presencia personal'}")
        print(f"   ⚠️ Riesgo: {top_nicho['riesgo_saturacion']}")
        print(f"   🎯 Score refinado: {top_nicho['potencial_total_refinado']}/100")
        
    else:
        print(f"\n❌ NINGÚN NICHO CUMPLE LOS CRITERIOS DE CALIDAD")
        print(f"   Analizados: {len(keywords)}")
        print(f"   Descartados: {len(descartados_list)}")
        print("\n💡 Sugerencias:")
        print("   - Prueba keywords más específicas")
        print("   - Busca nichos con mayor potencial de monetización")
        print("   - Considera nichos con mejor volumen de búsqueda")

    # Si el usuario pidió publicar en el Escritorio o en una carpeta personalizada, copiar los archivos
    try:
        if out_path and (args.publish_desktop or args.publish_dir):
            if args.publish_dir:
                dest = args.publish_dir
            else:
                # Desktop default
                dest = str(Path.home() / 'Desktop' / 'Script Youtube')
            published = publish_results(out_path, dest)
            print(f"📤 Resultados publicados en: {published}")
    except Exception as e:
        print(f"⚠️ Error publicando resultados: {e}")


if __name__ == "__main__":
    main()
