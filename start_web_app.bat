@echo off
echo 🚀 Iniciando aplicación web de análisis de nichos...
echo.

REM Instalar dependencias si no están instaladas
echo 📦 Verificando dependencias...
pip install -r requirements_web.txt

REM Verificar que las dependencias del proyecto YouTube estén instaladas
echo 📦 Verificando dependencias del proyecto YouTube...
if exist "proyecto_youtube\requirements.txt" (
    pip install -r proyecto_youtube\requirements.txt
)

echo.
echo 🎯 Iniciando servidor web...
echo 📱 Una vez iniciado, abre tu navegador en: http://localhost:5000
echo 🎯 Ve a la sección Discovery: http://localhost:5000/discovery
echo.

python web_app.py

pause
