"""
Interactive runner para análisis (flujo):

- Pregunta si usar Google Trends
- Si sí: pide cuántas tendencias traer
- Si no: pide cuántas keywords introducir manualmente y las lee
- Para cada keyword pregunta si ejecutar el análisis ahora

El script propondrá instalar dependencias si faltan.
"""

import sys
import os
import importlib
import subprocess


def install_dependencies():
    deps = ["google-api-python-client", "pytrends"]
    print("Instalando dependencias: ", ", ".join(deps))
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + deps)
        print("Instalación completada")
        return True
    except Exception as e:
        print(f"Fallo al instalar dependencias: {e}")
        return False


def safe_import_analyzer():
    try:
        mod = importlib.import_module('niche_analyzer_ultimate')
        NicheAnalyzerUltimate = getattr(mod, 'NicheAnalyzerUltimate')
        return NicheAnalyzerUltimate
    except Exception as e:
        print(f"No se pudo importar 'niche_analyzer_ultimate': {e}")
        return None


def interactive_flow():
    print("🔎 RUNNER INTERACTIVO - Análisis por keyword")

    use_trends = input("¿Deseas usar Google Trends para obtener keywords? (s/n): ").strip().lower() == 's'

    NicheAnalyzerUltimate = safe_import_analyzer()
    if NicheAnalyzerUltimate is None:
        print("Faltan dependencias o hay un error en el módulo.")
        install = input("¿Quieres que intente instalar dependencias ahora? (s/n): ").strip().lower() == 's'
        if install:
            ok = install_dependencies()
            if not ok:
                print("No se pudieron instalar las dependencias. El script no puede continuar.")
                return
            # reintentar importar
            NicheAnalyzerUltimate = safe_import_analyzer()
            if NicheAnalyzerUltimate is None:
                print("Aún no se puede importar el analizador. Abortando.")
                return
        else:
            print("Abortando por falta de dependencias.")
            return

    analyzer = NicheAnalyzerUltimate()
    analyzer.ultra_testing = True

    keywords = []

    if use_trends:
        try:
            n = int(input("¿Cuántas tendencias quieres obtener? (ej: 1): ").strip())
        except ValueError:
            print("Número inválido, usaré 1")
            n = 1

        # get_trending_keywords devuelve una lista (limitada por el modo testing)
        trending = analyzer.get_trending_keywords()
        if not trending:
            print("No se obtuvieron tendencias. Puedes introducir keywords manualmente.")
            use_trends = False
        else:
            print(f"Tendencias disponibles: {len(trending)}")
            for i, kw in enumerate(trending[:n], 1):
                print(f" {i}. {kw}")
            keywords = trending[:n]

    if not use_trends:
        try:
            count = int(input("¿Cuántas keywords vas a introducir manualmente? (ej: 1): ").strip())
        except ValueError:
            count = 1
        for i in range(count):
            kw = input(f"Introduce keyword #{i+1}: ").strip()
            if kw:
                keywords.append(kw)

    if not keywords:
        print("No hay keywords para analizar. Saliendo.")
        return

    print(f"\nSe analizarán {len(keywords)} keyword(s).")
    for kw in keywords:
        run_now = input(f"¿Ejecutar análisis para '{kw}' ahora? (s/n): ").strip().lower() == 's'
        if run_now:
            try:
                analyzer.run_single_keyword(kw)
            except Exception as e:
                print(f"Error al analizar '{kw}': {e}")
        else:
            print(f"Saltado '{kw}'")


if __name__ == '__main__':
    interactive_flow()
