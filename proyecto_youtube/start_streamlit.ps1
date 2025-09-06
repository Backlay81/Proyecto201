# 🚀 FASE 2: Iniciar Dashboard Streamlit Completo
# Proyecto YouTube - Análisis de Nichos y Canales

Write-Host "🎯 Iniciando YouTube Analyzer Pro - Fase 2" -ForegroundColor Green
Write-Host "📊 Dashboard con tabs para Nichos y Canales" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Yellow

# Verificar que streamlit está instalado
try {
    $streamlitVersion = python -c "import streamlit; print(streamlit.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Streamlit instalado: v$streamlitVersion" -ForegroundColor Green
    } else {
        throw "Streamlit no encontrado"
    }
} catch {
    Write-Host "❌ Error: Streamlit no está instalado" -ForegroundColor Red
    Write-Host "📦 Instala con: pip install streamlit" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎯 COMPONENTES DE FASE 2:" -ForegroundColor Magenta
Write-Host "  ✅ Dashboard con 3 tabs principales" -ForegroundColor Green
Write-Host "  ✅ Análisis de Nichos interactivo" -ForegroundColor Green
Write-Host "  ✅ Búsqueda de Canales avanzada" -ForegroundColor Green
Write-Host "  ✅ Visualización de datos con gráficos" -ForegroundColor Green
Write-Host "  ✅ Integración con base de datos" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Iniciando servidor Streamlit..." -ForegroundColor Green
Write-Host "📱 El dashboard estará disponible en: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏹️  Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Yellow

# Ejecutar Streamlit con el nuevo dashboard
streamlit run streamlit_app.py --server.headless true --server.port 8501
