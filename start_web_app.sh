#!/bin/bash

echo "🚀 Iniciando aplicación web de análisis de nichos..."
echo ""

# Instalar dependencias si no están instaladas
echo "📦 Verificando dependencias..."
pip install -r requirements_web.txt

# Verificar que las dependencias del proyecto YouTube estén instaladas
echo "📦 Verificando dependencias del proyecto YouTube..."
if [ -f "proyecto_youtube/requirements.txt" ]; then
    pip install -r proyecto_youtube/requirements.txt
fi

echo ""
echo "🎯 Iniciando servidor web..."
echo "📱 Una vez iniciado, abre tu navegador en: http://localhost:5000"
echo "🎯 Ve a la sección Discovery: http://localhost:5000/discovery"
echo ""

python web_app.py
