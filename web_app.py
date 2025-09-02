from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import json
from datetime import datetime
import subprocess
import threading

# Agregar el directorio del proyecto al path
current_dir = os.path.dirname(os.path.abspath(__file__))
youtube_project_path = os.path.join(current_dir, 'proyecto_youtube')
sys.path.append(youtube_project_path)

app = Flask(__name__,
            template_folder='../mockup_site',
            static_folder='../mockup_site')

# Variable global para almacenar el estado del análisis
analysis_status = {
    'running': False,
    'progress': 0,
    'message': '',
    'results': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/discovery')
def discovery():
    return render_template('discovery.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_niche():
    global analysis_status

    if analysis_status['running']:
        return jsonify({'error': 'Analysis already running'}), 400

    data = request.get_json()
    category = data.get('category', '').strip()

    if not category:
        return jsonify({'error': 'Category is required'}), 400

    # Iniciar análisis en un hilo separado
    thread = threading.Thread(target=run_analysis, args=(category,))
    thread.daemon = True
    thread.start()

    return jsonify({'message': 'Analysis started', 'category': category})

@app.route('/api/status')
def get_status():
    global analysis_status
    return jsonify(analysis_status)

@app.route('/api/results')
def get_results():
    global analysis_status
    if analysis_status['results']:
        return jsonify(analysis_status['results'])
    return jsonify({'error': 'No results available'}), 404

def run_analysis(category):
    global analysis_status

    try:
        analysis_status['running'] = True
        analysis_status['progress'] = 0
        analysis_status['message'] = f'Starting analysis for: {category}'

        # Importar el analizador de nichos
        from nichos_youtube import NicheAnalyzerUltimate

        analysis_status['progress'] = 10
        analysis_status['message'] = 'Initializing analyzer...'

        # Crear instancia del analizador
        analyzer = NicheAnalyzerUltimate()

        analysis_status['progress'] = 20
        analysis_status['message'] = 'Loading keywords...'

        # Ejecutar análisis completo
        results = analyzer.run_complete_analysis()

        analysis_status['progress'] = 80
        analysis_status['message'] = 'Generating report...'

        if results:
            # Generar reporte
            analyzer.generate_report(results)

            analysis_status['progress'] = 90
            analysis_status['message'] = 'Exporting results...'

            # Exportar resultados
            analyzer.export_results(results)

            analysis_status['progress'] = 100
            analysis_status['message'] = 'Analysis completed successfully!'
            analysis_status['results'] = results
        else:
            analysis_status['message'] = 'No results obtained'

    except Exception as e:
        analysis_status['message'] = f'Error during analysis: {str(e)}'
        print(f"Error: {e}")

    finally:
        analysis_status['running'] = False

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('../mockup_site/assets', filename)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../mockup_site', filename)

if __name__ == '__main__':
    print("🚀 Starting Niche Analysis Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎯 Navigate to: http://localhost:5000/discovery")
    app.run(debug=True, host='0.0.0.0', port=5000)
