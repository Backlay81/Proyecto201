# 🌐 Aplicación Web de Análisis de Nichos

Esta aplicación web te permite ejecutar el análisis de nichos de YouTube desde una interfaz visual atractiva en tu navegador local.

## 🚀 Inicio Rápido

### Windows
```bash
# Ejecuta el script de inicio
start_web_app.bat
```

### Linux/Mac
```bash
# Ejecuta el script de inicio
chmod +x start_web_app.sh
./start_web_app.sh
```

### Manual
```bash
# Instalar dependencias
pip install -r requirements_web.txt
pip install -r proyecto_youtube/requirements.txt

# Ejecutar la aplicación
python web_app.py
```

## 📱 Uso de la Aplicación

1. **Abrir el navegador**: Ve a `http://localhost:5000`
2. **Ir a Discovery**: Haz clic en "Niche Discovery" o ve directamente a `http://localhost:5000/discovery`
3. **Ingresar categoría**: Escribe una categoría amplia (ej: "health", "technology", "pets")
4. **Ejecutar análisis**: Haz clic en "Analyze Potential"
5. **Ver resultados**: Los resultados aparecerán en la interfaz con gráficos y tablas

## 🎯 Características

- ✅ **Interfaz moderna**: Diseño atractivo con navegación intuitiva
- ✅ **Análisis en tiempo real**: Progreso del análisis en vivo
- ✅ **Resultados visuales**: Tablas comparativas y estadísticas
- ✅ **Exportación automática**: Genera CSV y Markdown automáticamente
- ✅ **API Status**: Monitoreo del uso de APIs
- ✅ **Responsive**: Funciona en desktop y móvil

## 📊 Qué Analiza

- **Tendencias de Google**: Popularidad de keywords
- **Datos de YouTube**: Views, likes, comments de videos reales
- **Competencia**: Nivel de saturación del nicho
- **Monetización**: Potencial de ingresos por nicho
- **Automatización**: Facilidad para crear contenido

## 🔧 Configuración

Asegúrate de tener configuradas las APIs:

1. **YouTube Data API v3**: API key en `proyecto_youtube/config/youtube_config.py`
2. **Google Trends**: Configurado en el script de análisis

## 📁 Estructura de Archivos

```
Proyecto 201/
├── web_app.py              # Aplicación web principal
├── requirements_web.txt    # Dependencias web
├── start_web_app.bat       # Script inicio Windows
├── start_web_app.sh        # Script inicio Linux/Mac
├── mockup_site/            # Archivos HTML/CSS/JS
└── proyecto_youtube/       # Scripts de análisis
```

## 🛠️ Solución de Problemas

### Error de importación
```bash
pip install -r requirements_web.txt
pip install -r proyecto_youtube/requirements.txt
```

### Puerto ocupado
Cambia el puerto en `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### API Key no configurada
Verifica que tengas tu API key de YouTube en el archivo de configuración.

## 📈 Resultados

Los resultados se guardan automáticamente en:
- `nichos_trends_YYYYMMDD_HHMMSS.csv`
- `nichos_trends_YYYYMMDD_HHMMSS.md`

¡Disfruta analizando nichos de manera visual! 🎯</content>
<parameter name="filePath">c:\Users\javie\AndroidStudioProjects\Proyecto 201\WEB_APP_README.md
