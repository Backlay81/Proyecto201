#!/usr/bin/env python3
"""
NICHOS WEB ANALYZER
===================
Script para análisis de nichos web usando Google Trends y (futuro) Google Ads Keyword Planner.

Características:
- Análisis de keywords para crear webs de nicho
- Métricas de Google Trends: interés relativo y tendencias
- Sistema inteligente de rate limiting para evitar bloqueos
- Reintentos automáticos con backoff exponencial
- Preparado para integrar Google Ads Keyword Planner API (cuando esté disponible)
- Exportación a CSV, Parquet y Markdown

Rate Limiting:
- Delay configurable entre peticiones (default: 5s)
- Backoff exponencial en caso de rate limit (429)
- Reintentos automáticos (default: 3)
- Manejo inteligente de errores

Autor: Proyecto 201 digital
Fecha: 2025-09-02
"""

import os
import sys
import time
import argparse
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nichos_web.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class WebNicheAnalyzer:
    """
    Analizador de nichos web usando Google Trends y Google Ads (futuro)
    """

    def __init__(self, seeds_file: str = "seeds_web.txt", out_dir: str = "./out/web/", 
                 request_delay: float = 5.0, max_retries: int = 3):
        """
        Inicializa el analizador de nichos web

        Args:
            seeds_file: Archivo con keywords semilla
            out_dir: Directorio de salida
            request_delay: Segundos entre peticiones a Google Trends
            max_retries: Número máximo de reintentos por keyword
        """
        self.seeds_file = seeds_file
        self.out_dir = Path(out_dir)
        self.results = []
        
        # Configuración de rate limiting
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.retry_count = 0

        # Configurar PyTrends (Google Trends)
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl='es-ES', tz=360)
            self.trends_available = True
            logger.info("✅ Google Trends inicializado correctamente")
            logger.info(f"⏱️  Delay entre peticiones: {self.request_delay}s")
            logger.info(f"🔄 Máximo reintentos: {self.max_retries}")
        except ImportError:
            logger.error("❌ Error: pytrends no está instalado")
            self.pytrends = None
            self.trends_available = False

        # Google Ads API - preparado para el futuro
        self.ads_api_available = False
        logger.info("⚠️  Google Ads API no configurado (pendiente de implementación)")

        # Crear directorio de salida con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        self.output_dir = self.out_dir / timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directorio de salida: {self.output_dir}")

    def load_seed_keywords(self) -> List[str]:
        """
        Carga las keywords semilla desde el archivo

        Returns:
            Lista de keywords semilla
        """
        try:
            if not os.path.exists(self.seeds_file):
                logger.error(f"❌ Archivo {self.seeds_file} no encontrado")
                return []

            with open(self.seeds_file, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            logger.info(f"📝 Cargadas {len(keywords)} keywords semilla desde {self.seeds_file}")
            return keywords

        except Exception as e:
            logger.error(f"❌ Error cargando keywords: {str(e)}")
            return []

    def get_trends_data(self, keyword: str) -> Dict:
        """
        Obtiene datos de tendencias de Google Trends con rate limiting y reintentos

        Args:
            keyword: Keyword a analizar

        Returns:
            Diccionario con datos de tendencias
        """
        if not self.trends_available:
            return {
                'trend_score': 0.0,
                'trend_direction': 'unknown',
                'relative_interest': 0,
                'trend_error': 'PyTrends not available'
            }

        # Sistema de reintentos con backoff exponencial
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"📊 Consultando Google Trends para '{keyword}' (intento {attempt + 1}/{self.max_retries + 1})")
                
                # Obtener interés a lo largo del tiempo (últimos 12 meses)
                self.pytrends.build_payload([keyword], timeframe='today 12-m', geo='ES')

                # Obtener datos de interés
                interest_data = self.pytrends.interest_over_time()

                if interest_data.empty or keyword not in interest_data.columns:
                    logger.warning(f"⚠️  No hay datos de tendencias para '{keyword}'")
                    return {
                        'trend_score': 0.0,
                        'trend_direction': 'no_data',
                        'relative_interest': 0,
                        'trend_error': None
                    }

                # Calcular métricas
                values = interest_data[keyword].values
                relative_interest = int(values.mean()) if len(values) > 0 else 0

                if len(values) < 2:
                    trend_score = 0.0
                    direction = 'stable'
                else:
                    # Comparar último trimestre vs anterior
                    recent_avg = values[-3:].mean() if len(values) >= 3 else values[-1]
                    older_avg = values[:-3].mean() if len(values) > 3 else values[0]
                    
                    if older_avg > 0:
                        trend_score = (recent_avg - older_avg) / older_avg
                    else:
                        trend_score = 0.0

                    # Determinar dirección de la tendencia
                    if trend_score > 0.15:
                        direction = 'up'
                    elif trend_score < -0.15:
                        direction = 'down'
                    else:
                        direction = 'stable'

                logger.info(f"✅ Datos obtenidos exitosamente para '{keyword}'")
                return {
                    'trend_score': round(trend_score, 3),
                    'trend_direction': direction,
                    'relative_interest': relative_interest,
                    'trend_error': None
                }

            except Exception as e:
                error_msg = str(e)
                
                # Si es error 429 (rate limit), aplicar backoff exponencial
                if "429" in error_msg or "TooManyRequestsError" in error_msg:
                    if attempt < self.max_retries:
                        wait_time = self.request_delay * (2 ** attempt)  # Backoff exponencial
                        logger.warning(f"⚠️  Rate limit alcanzado. Esperando {wait_time:.1f}s antes del siguiente intento...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"❌ Rate limit persistente para '{keyword}' después de {self.max_retries + 1} intentos")
                else:
                    logger.warning(f"⚠️  Error obteniendo trends para '{keyword}': {error_msg}")
                
                # Si no es el último intento, esperar antes del siguiente
                if attempt < self.max_retries:
                    wait_time = self.request_delay
                    logger.info(f"⏱️  Esperando {wait_time}s antes del siguiente intento...")
                    time.sleep(wait_time)
                else:
                    # Último intento fallido
                    return {
                        'trend_score': 0.0,
                        'trend_direction': 'error',
                        'relative_interest': 0,
                        'trend_error': error_msg
                    }

        # Este código nunca debería alcanzarse, pero por si acaso
        return {
            'trend_score': 0.0,
            'trend_direction': 'error',
            'relative_interest': 0,
            'trend_error': 'Maximum retries exceeded'
        }

    def get_ads_data(self, keyword: str) -> Dict:
        """
        Obtiene datos de Google Ads Keyword Planner (STUB - implementar cuando esté disponible)

        Args:
            keyword: Keyword a analizar

        Returns:
            Diccionario con datos de Ads (simulados por ahora)
        """
        if self.ads_api_available:
            # TODO: Implementar cuando tengamos acceso a Google Ads API
            pass
        
        # Por ahora, generar datos simulados basados en características de la keyword
        import random
        
        keyword_length = len(keyword.split())
        has_commercial_intent = any(word in keyword.lower() for word in [
            'comprar', 'precio', 'barato', 'oferta', 'mejor', 'comparar', 'review'
        ])
        
        # Simular volumen de búsqueda (500-50k)
        base_volume = random.randint(500, 50000)
        if keyword_length > 3:
            base_volume = int(base_volume * 0.6)  # Keywords largas menos volumen
        if has_commercial_intent:
            base_volume = int(base_volume * 1.3)  # Intent comercial más volumen
        
        # Simular CPC (0.05-3.0)
        base_cpc = random.uniform(0.05, 3.0)
        if has_commercial_intent:
            base_cpc *= 2.0  # Intent comercial más caro
        if keyword_length > 3:
            base_cpc *= 0.8  # Keywords largas más baratas
        
        # Simular competencia (0.0-1.0)
        base_competition = random.uniform(0.1, 1.0)
        if has_commercial_intent:
            base_competition *= 1.2
        base_competition = min(base_competition, 1.0)
        
        return {
            'search_volume': int(base_volume),
            'cpc': round(base_cpc, 2),
            'competition_index': round(base_competition, 2),
            'data_source': 'simulated'  # Indicar que son datos simulados
        }

    def analyze_keyword(self, keyword: str) -> Dict:
        """
        Analiza una keyword completa

        Args:
            keyword: Keyword a analizar

        Returns:
            Diccionario con todos los datos del análisis
        """
        logger.info(f"🔍 Analizando keyword: '{keyword}'")

        # Obtener datos de tendencias
        trends_data = self.get_trends_data(keyword)
        
        # Obtener datos de Ads
        ads_data = self.get_ads_data(keyword)

        # Calcular decisión
        decision = self.make_decision(ads_data, trends_data)

        result = {
            'keyword': keyword,
            'search_volume': ads_data['search_volume'],
            'cpc': ads_data['cpc'],
            'competition_index': ads_data['competition_index'],
            'trend_score': trends_data['trend_score'],
            'trend_direction': trends_data['trend_direction'],
            'relative_interest': trends_data['relative_interest'],
            'decision': decision,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': ads_data.get('data_source', 'real'),
            'trend_error': trends_data.get('trend_error')
        }

        return result

    def make_decision(self, ads_data: Dict, trends_data: Dict) -> str:
        """
        Toma una decisión basada en el análisis

        Args:
            ads_data: Datos de Google Ads
            trends_data: Datos de tendencias

        Returns:
            Decisión recomendada
        """
        volume = ads_data['search_volume']
        cpc = ads_data['cpc']
        competition = ads_data['competition_index']
        trend_direction = trends_data['trend_direction']
        trend_score = trends_data['trend_score']

        # Lógica de decisión para nichos web
        score = 0
        
        # Puntuación por volumen (peso: 40%)
        if volume >= 10000:
            score += 40
        elif volume >= 5000:
            score += 30
        elif volume >= 1000:
            score += 20
        else:
            score += 10
            
        # Puntuación por CPC (peso: 25%)
        if cpc <= 0.5:
            score += 25
        elif cpc <= 1.0:
            score += 20
        elif cpc <= 2.0:
            score += 15
        else:
            score += 5
            
        # Puntuación por competencia (peso: 25%)
        if competition <= 0.3:
            score += 25
        elif competition <= 0.5:
            score += 20
        elif competition <= 0.7:
            score += 15
        else:
            score += 5
            
        # Puntuación por tendencia (peso: 10%)
        if trend_direction == 'up':
            score += 10
        elif trend_direction == 'stable':
            score += 7
        else:
            score += 3

        # Decisión final
        if score >= 75:
            return "RECOMENDADO"
        elif score >= 50:
            return "EVALUAR"
        else:
            return "DESCARTAR"

    def run_analysis(self) -> pd.DataFrame:
        """
        Ejecuta el análisis completo

        Returns:
            DataFrame con todos los resultados
        """
        logger.info("🚀 Iniciando análisis de nichos web")
        start_time = time.time()

        # Cargar keywords semilla
        keywords = self.load_seed_keywords()
        if not keywords:
            logger.error("❌ No se pudieron cargar keywords semilla")
            return pd.DataFrame()

        logger.info(f"📊 Analizando {len(keywords)} keywords...")

        # Analizar cada keyword
        for i, keyword in enumerate(keywords, 1):
            logger.info(f"🔄 Progreso: {i}/{len(keywords)} - {keyword}")
            result = self.analyze_keyword(keyword)
            self.results.append(result)

        # Analizar cada keyword con rate limiting inteligente
        for i, keyword in enumerate(keywords, 1):
            logger.info(f"🔄 Progreso: {i}/{len(keywords)} - {keyword}")
            result = self.analyze_keyword(keyword)
            self.results.append(result)

            # Pausa inteligente entre keywords (solo si no hubo error reciente)
            if i < len(keywords):
                if result.get('trend_error') and ('429' in result['trend_error'] or 'TooManyRequestsError' in result['trend_error']):
                    # Si hubo rate limit, esperar más tiempo
                    wait_time = self.request_delay * 2
                    logger.info(f"⏱️  Rate limit detectado. Esperando {wait_time}s antes de continuar...")
                else:
                    # Espera normal
                    wait_time = self.request_delay
                    logger.info(f"⏱️  Esperando {wait_time}s antes de la siguiente keyword...")
                
                time.sleep(wait_time)

        # Crear DataFrame
        df = pd.DataFrame(self.results)

        # Calcular tiempo de ejecución
        execution_time = time.time() - start_time
        logger.info(f"⏰ Tiempo de ejecución: {execution_time:.2f} segundos")
        
        return df

    def export_results(self, df: pd.DataFrame, export_parquet: bool = False, export_markdown: bool = False) -> None:
        """
        Exporta los resultados a CSV y opcionalmente Parquet y Markdown

        Args:
            df: DataFrame con resultados
            export_parquet: Si exportar también a Parquet
            export_markdown: Si exportar también a Markdown
        """
        if df.empty:
            logger.warning("⚠️  No hay datos para exportar")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Exportar a CSV
        csv_file = self.output_dir / f"nichos_web_analisis_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        logger.info(f"✅ Exportado CSV: {csv_file}")

        # Exportar a Parquet si se solicita
        if export_parquet:
            try:
                parquet_file = self.output_dir / f"nichos_web_analisis_{timestamp}.parquet"
                df.to_parquet(parquet_file, index=False)
                logger.info(f"✅ Exportado Parquet: {parquet_file}")
            except ImportError:
                logger.warning("⚠️  pyarrow no disponible, omitiendo exportación Parquet")
            except Exception as e:
                logger.warning(f"⚠️  Error exportando Parquet: {str(e)}")

        # Exportar a Markdown si se solicita
        if export_markdown:
            try:
                md_file = self.output_dir / f"nichos_web_analisis_{timestamp}.md"
                self.export_to_markdown(df, md_file)
                logger.info(f"✅ Exportado Markdown: {md_file}")
            except Exception as e:
                logger.warning(f"⚠️  Error exportando Markdown: {str(e)}")

        # Mostrar resumen
        self.show_summary(df)

    def show_summary(self, df: pd.DataFrame) -> None:
        """
        Muestra un resumen de los resultados

        Args:
            df: DataFrame con resultados
        """
        print("\n" + "="*60)
        print("📊 RESUMEN DEL ANÁLISIS DE NICHOS WEB")
        print("="*60)
        
        total = len(df)
        recomendados = len(df[df['decision'] == 'RECOMENDADO'])
        evaluar = len(df[df['decision'] == 'EVALUAR'])
        descartar = len(df[df['decision'] == 'DESCARTAR'])
        
        print(f"📝 Keywords analizadas: {total}")
        print(f"✅ RECOMENDADOS: {recomendados} ({recomendados/total*100:.1f}%)")
        print(f"🔍 EVALUAR: {evaluar} ({evaluar/total*100:.1f}%)")
        print(f"❌ DESCARTAR: {descartar} ({descartar/total*100:.1f}%)")
        
        if recomendados > 0:
            print(f"\n🏆 TOP KEYWORDS RECOMENDADAS:")
            top_keywords = df[df['decision'] == 'RECOMENDADO'].nlargest(3, 'search_volume')
            for idx, row in top_keywords.iterrows():
                print(f"   • {row['keyword']}: {row['search_volume']:,} búsquedas, CPC €{row['cpc']}")
        
        print(f"\n📈 Tendencias positivas: {len(df[df['trend_direction'] == 'up'])}")
        print(f"📊 Volumen promedio: {df['search_volume'].mean():,.0f} búsquedas/mes")
        print(f"💰 CPC promedio: €{df['cpc'].mean():.2f}")

    def export_to_markdown(self, df: pd.DataFrame, md_file: Path) -> None:
        """
        Exporta los resultados a formato Markdown con formato visual atractivo

        Args:
            df: DataFrame con resultados
            md_file: Ruta del archivo Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Crear contenido Markdown con formato visual atractivo
        md_content = []
        md_content.append("# 📊 **NICHOS WEB ANALYZER** - Reporte de Análisis")
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append(f"📅 **Fecha de análisis:** {timestamp}")
        md_content.append(f"🔢 **Keywords analizadas:** {len(df)}")
        md_content.append("")
        md_content.append("---")
        md_content.append("")

        # Estadísticas generales con colores y iconos
        total = len(df)
        recomendados = len(df[df['decision'] == 'RECOMENDADO'])
        evaluar = len(df[df['decision'] == 'EVALUAR'])
        descartar = len(df[df['decision'] == 'DESCARTAR'])

        md_content.append("## 🎯 **ESTADÍSTICAS GENERALES**")
        md_content.append("")
        md_content.append("### 📈 **Resumen Ejecutivo**")
        md_content.append("")
        md_content.append(f"🔹 **Total keywords:** `{total}`")
        if recomendados > 0:
            md_content.append(f"✅ **Recomendadas:** `{recomendados}` ({recomendados/total*100:.1f}%) 🟢")
        else:
            md_content.append(f"✅ **Recomendadas:** `{recomendados}` ({recomendados/total*100:.1f}%)")
        md_content.append(f"🔍 **Para evaluar:** `{evaluar}` ({evaluar/total*100:.1f}%) 🟡")
        if descartar > 0:
            md_content.append(f"❌ **Descartadas:** `{descartar}` ({descartar/total*100:.1f}%) 🔴")
        else:
            md_content.append(f"❌ **Descartadas:** `{descartar}` ({descartar/total*100:.1f}%)")
        md_content.append("")

        # Métricas promedio con formato mejorado
        md_content.append("### 📊 **MÉTRICAS PROMEDIO**")
        md_content.append("")
        md_content.append("💡 **Indicadores clave de rendimiento:**")
        md_content.append("")
        md_content.append(f"🔹 **Volumen de búsqueda promedio:** `{df['search_volume'].mean():,.0f}` búsquedas/mes 📈")
        md_content.append(f"💰 **CPC promedio:** `€{df['cpc'].mean():.2f}` 💵")
        md_content.append(f"🏆 **Índice de competencia promedio:** `{df['competition_index'].mean():.2f}` ⚔️")
        md_content.append(f"📊 **Tendencias positivas:** `{len(df[df['trend_direction'] == 'up'])}` ↗️")
        md_content.append("")

        # Keywords recomendadas con formato destacado
        if recomendados > 0:
            md_content.append("## 🏆 **KEYWORDS RECOMENDADAS** 🟢")
            md_content.append("")
            md_content.append("🎯 **¡Estas son las mejores oportunidades!**")
            md_content.append("")
            top_keywords = df[df['decision'] == 'RECOMENDADO'].nlargest(5, 'search_volume')
            for idx, row in top_keywords.iterrows():
                md_content.append(f"### 🥇 **{row['keyword']}**")
                md_content.append("")
                md_content.append("**📊 Métricas principales:**")
                md_content.append(f"- 🔍 **Volumen de búsqueda:** `{row['search_volume']:,}` búsquedas/mes")
                md_content.append(f"- 💰 **CPC:** `€{row['cpc']}`")
                md_content.append(f"- 🏆 **Competencia:** `{row['competition_index']}`")
                md_content.append(f"- ✅ **Decisión:** **{row['decision']}** 🟢")
                md_content.append("")

        # Keywords para evaluar
        if evaluar > 0:
            md_content.append("## 🔍 **KEYWORDS PARA EVALUAR** 🟡")
            md_content.append("")
            md_content.append("⚠️ **Estas requieren análisis adicional**")
            md_content.append("")
            eval_keywords = df[df['decision'] == 'EVALUAR'].nlargest(5, 'search_volume')
            for idx, row in eval_keywords.iterrows():
                md_content.append(f"### 📋 **{row['keyword']}**")
                md_content.append("")
                md_content.append("**📊 Métricas principales:**")
                md_content.append(f"- 🔍 **Volumen de búsqueda:** `{row['search_volume']:,}` búsquedas/mes")
                md_content.append(f"- 💰 **CPC:** `€{row['cpc']}`")
                md_content.append(f"- 🏆 **Competencia:** `{row['competition_index']}`")
                md_content.append(f"- 🔍 **Decisión:** **{row['decision']}** 🟡")
                md_content.append("")

        # Keywords descartadas
        if descartar > 0:
            md_content.append("## ❌ **KEYWORDS DESCARTADAS** 🔴")
            md_content.append("")
            md_content.append("🚫 **No recomendadas para desarrollo**")
            md_content.append("")
            desc_keywords = df[df['decision'] == 'DESCARTAR'].nlargest(3, 'search_volume')
            for idx, row in desc_keywords.iterrows():
                md_content.append(f"### 🚫 **{row['keyword']}**")
                md_content.append("")
                md_content.append("**📊 Métricas principales:**")
                md_content.append(f"- 🔍 **Volumen de búsqueda:** `{row['search_volume']:,}` búsquedas/mes")
                md_content.append(f"- � **CPC:** `€{row['cpc']}`")
                md_content.append(f"- 🏆 **Competencia:** `{row['competition_index']}`")
                md_content.append(f"- ❌ **Decisión:** **{row['decision']}** 🔴")
                md_content.append("")

        # Tabla completa con mejor formato
        md_content.append("## 📋 **TABLA COMPLETA DE RESULTADOS**")
        md_content.append("")
        md_content.append("📊 **Vista detallada de todas las keywords analizadas:**")
        md_content.append("")
        md_content.append("| 🔍 Keyword | 📈 Volumen | 💰 CPC | 🏆 Competencia | ✅ Decisión |")
        md_content.append("|------------|------------|--------|---------------|-------------|")

        for idx, row in df.iterrows():
            decision_icon = "🟢" if row['decision'] == 'RECOMENDADO' else "🟡" if row['decision'] == 'EVALUAR' else "🔴"
            md_content.append(f"| **{row['keyword']}** | `{row['search_volume']:,}` | `€{row['cpc']}` | `{row['competition_index']}` | **{row['decision']}** {decision_icon} |")

        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## 🎉 **ANÁLISIS COMPLETADO**")
        md_content.append("")
        md_content.append("✅ **Reporte generado automáticamente por NICHOS WEB ANALYZER**")
        md_content.append("📁 **Archivos generados:** CSV + Markdown")
        md_content.append("🔗 **Proyecto:** [Proyecto 201 digital](https://github.com/Backlay81/Proyecto201)")
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("*💡 **Consejo:** Las keywords marcadas con 🟢 son las más prometedoras para desarrollar nichos web*")

        # Escribir archivo
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))


def main():
    """
    Función principal
    """
    parser = argparse.ArgumentParser(
        description="Analizador de nichos web usando Google Trends y Google Ads",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--seeds-file',
        default='seeds_web.txt',
        help='Archivo con keywords semilla (default: seeds_web.txt)'
    )
    
    parser.add_argument(
        '--out-dir',
        default='./out/web/',
        help='Directorio de salida (default: ./out/web/)'
    )
    
    parser.add_argument(
        '--parquet',
        action='store_true',
        help='Exportar también a formato Parquet'
    )
    
    parser.add_argument(
        '--markdown',
        action='store_true',
        help='Exportar también a formato Markdown'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=5.0,
        help='Segundos entre peticiones a Google Trends (default: 5.0)'
    )
    
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Número máximo de reintentos por keyword (default: 3)'
    )
    
    args = parser.parse_args()

    print("🔥 NICHOS WEB ANALYZER")
    print("=" * 50)
    print(f"📂 Seeds file: {args.seeds_file}")
    print(f"📁 Output dir: {args.out_dir}")
    print(f"📦 Parquet export: {'Sí' if args.parquet else 'No'}")
    print(f"📝 Markdown export: {'Sí' if args.markdown else 'No'}")
    print(f"⏱️  Delay entre peticiones: {args.delay}s")
    print(f"🔄 Máximo reintentos: {args.max_retries}")
    print("=" * 50)

    # Inicializar analizador
    analyzer = WebNicheAnalyzer(
        seeds_file=args.seeds_file,
        out_dir=args.out_dir,
        request_delay=args.delay,
        max_retries=args.max_retries
    )

    try:
        # Ejecutar análisis
        results_df = analyzer.run_analysis()

        if not results_df.empty:
            # Exportar resultados
            analyzer.export_results(results_df, export_parquet=args.parquet, export_markdown=args.markdown)
            print(f"\n✅ Análisis completado exitosamente")
            print(f"📁 Resultados guardados en: {analyzer.output_dir}")
        else:
            print("\n❌ Error: No se pudieron obtener resultados")

    except KeyboardInterrupt:
        print("\n⏹️  Análisis interrumpido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en el análisis: {e}")
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
