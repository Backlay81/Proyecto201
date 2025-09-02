# 🎥 Nichos YouTube Analyzer

Analizador de nichos YouTube que utiliza la YouTube Data API para identificar oportunidades de contenido rentables en la plataforma.

## 📋 Características

- **Análisis de Búsqueda**: Resultados de búsqueda en YouTube con estadísticas completas
- **Métricas de Engagement**: Views, likes, comentarios y ratios de monetización
- **Evaluación de Saturación**: Análisis de competencia y riesgo de saturación
- **Automatización**: Detección de nichos susceptibles de automatización
- **Decisiones Inteligentes**: Recomendaciones basadas en algoritmos de scoring

## 🚀 Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar YouTube Data API:**
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea un proyecto o selecciona uno existente
   - Habilita la YouTube Data API v3
   - Crea credenciales (API Key)
   - Configura la variable de entorno:
   ```bash
   export YOUTUBE_API_KEY="tu_api_key_aqui"
   ```

## 📝 Uso

### 1. Preparar Keywords

Edita el archivo `keywords_youtube.txt` con las keywords que quieres analizar:

```
finanzas personales
review productos tecnológicos
cocina saludable
fitness en casa
viajes económicos
```

### 2. Ejecutar el Análisis

```bash
python nichos_youtube.py
```

### 3. Revisar Resultados

Los resultados se exportan automáticamente a:
- `nichos_youtube_analisis_YYYYMMDD_HHMMSS.csv`
- `nichos_youtube_analisis_YYYYMMDD_HHMMSS.parquet`

## 📊 Columnas de Output

| Columna | Descripción |
|---------|-------------|
| `keyword` | La keyword analizada |
| `results_count` | Número de videos encontrados |
| `median_views` | Views medianos de los videos |
| `pct75_views` | Percentil 75 de views |
| `max_views` | Máximo de views encontrado |
| `monetizable_ratio` | Ratio de videos con >10k views |
| `automatizable` | Si el nicho es automatizable |
| `saturation_risk` | Riesgo de saturación (low/medium/high) |
| `opportunity_score` | Score calculado de oportunidad |
| `decision` | Recomendación automática |

## 🎯 Interpretación de Resultados

### Decisiones:
- **EXCELENTE**: Alto potencial de views y monetización, bajo riesgo
- **BUENA**: Buena oportunidad con potencial sólido
- **ACEPTABLE**: Oportunidad moderada
- **OBSERVAR**: Potencial con bajo riesgo de saturación
- **MODERADA**: Revisar estrategia de diferenciación
- **CONSIDERAR**: Alta competencia, difícil entrada
- **REVISAR**: Requiere análisis manual detallado
- **DESCARTAR**: Muy baja actividad o potencial

### Métricas Clave:
- **Median Views**: Views promedio de los videos (meta: >25k)
- **Monetizable Ratio**: % de videos con potencial de monetización (meta: >0.3)
- **Saturation Risk**: Nivel de competencia en el nicho

## ⚙️ Configuración

### Archivo keywords_youtube.txt
- Una keyword por línea
- Líneas que empiecen con `#` son comentarios
- Keywords vacías son ignoradas

### Variables de Entorno
```bash
export YOUTUBE_API_KEY="tu_clave_api"
```

### Logging
Los logs se guardan en `nichos_youtube.log` con información detallada.

## 📈 Limitaciones de API

- **Cuota Diaria**: 10,000 unidades por día
- **Costo por Búsqueda**: 100 unidades
- **Costo por Detalles**: 1 unidad por video
- **Límite de Resultados**: Máximo 50 por búsqueda

## 🔧 Dependencias

- `google-api-python-client`: API de YouTube
- `pandas`: Manipulación de datos
- `pyarrow`: Exportación Parquet
- `requests`: HTTP requests
- `openpyxl`: Soporte Excel

## 📊 Algoritmo de Scoring

El score de oportunidad se calcula ponderando:

- **Views (40%)**: Potencial de alcance
- **Monetizable Ratio (40%)**: Capacidad de generar ingresos
- **Saturation Risk (20%)**: Nivel de competencia

## 🛠️ Desarrollo Futuro

- [ ] Integración con Google Trends para validación
- [ ] Análisis de tendencias temporales
- [ ] Detección de patrones de títulos exitosos
- [ ] Análisis de competencia por canal
- [ ] Dashboard web para visualización
- [ ] API REST para integración

## ⚠️ Consideraciones

- **Cumple las Políticas**: Revisa las políticas de uso de YouTube Data API
- **Gestión de Cuota**: Monitorea el uso de API para evitar límites
- **Datos Actuales**: Los resultados reflejan el estado actual de YouTube
- **Interpretación**: Las recomendaciones son guías, no decisiones absolutas

## 📄 Licencia

Este proyecto es de uso personal. Revisa las políticas de uso de las APIs de Google antes de usar en producción.

## 🤝 Contribución

Para mejoras o correcciones, por favor crea un issue o pull request.
