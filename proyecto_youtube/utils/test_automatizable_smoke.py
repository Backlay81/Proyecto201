import json
import sys
from pathlib import Path

# Asegurar que la carpeta raíz del workspace está en sys.path para importar el paquete local
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from proyecto_youtube.utils.niche_analyzer_ultimate import NicheAnalyzerUltimate


def run_tests():
    an = NicheAnalyzerUltimate()
    # Desactivar conexiones externas para la prueba
    an.trends_available = False
    an.youtube = None

    print('--- Test 1: videos con señales (ES) ---')
    mock_videos = [
        {'snippet': {'title': 'Tutorial: Cómo usar un script', 'description': 'Paso a paso para automatizar tareas', 'tags': ['tutorial','script']}},
        {'snippet': {'title': 'Review del mejor producto', 'description': 'Análisis y características', 'tags': ['review','mejor']}},
        {'snippet': {'title': 'Vlog sin señales', 'description': 'Un día normal', 'tags': []}},
    ]
    res = an.analyze_automatizable_advanced(mock_videos, geo_region='ES')
    print('Status:', res.get('automatizable_status'))
    print('Ratio:', res.get('automatizable_ratio'))
    print('Signals:', ', '.join(res.get('automatizable_signals', [])))
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print('\n--- Test 2: sin videos (vacio) ---')
    res2 = an.analyze_automatizable_advanced([], geo_region='ES')
    print('Status:', res2.get('automatizable_status'))
    print('Ratio:', res2.get('automatizable_ratio'))
    print('Signals:', ', '.join(res2.get('automatizable_signals', [])))
    print(json.dumps(res2, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    run_tests()
