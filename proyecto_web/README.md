# 🔍 Nichos Web Analyzer

Analizador de nichos web que combina datos de Google Ads Keyword Planner y Google Trends para identificar oportunidades de contenido web rentables.

## 📋 Características

- **Análisis de Keywords**: Volumen de búsqueda, CPC y competencia desde Google Ads
- **Tendencias Temporales**: Análisis de interés a lo largo del tiempo con Google Trends
- **Score de Oportunidad**: Algoritmo inteligente que combina múltiples factores
- **Decisiones Automáticas**: Recomendaciones basadas en criterios objetivos
- **Exportación Múltiple**: Resultados en CSV y Parquet

## 🚀 Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar Google Ads API** (opcional, pendiente):
   - Crear cuenta de desarrollador en Google Ads
   - Configurar credenciales OAuth
   - Actualizar configuración en el código

## 📝 Uso

### 1. Preparar Keywords Semilla

Edita el archivo `seeds_web.txt` con las keywords que quieres analizar:

```
finanzas personales
mejores productos tecnológicos
review criptomonedas
marketing digital
salud y bienestar
```

### 2. Ejecutar el Análisis

```bash
python nichos_web.py
```

### 3. Revisar Resultados

Los resultados se exportan automáticamente a:
- `nichos_web_analisis_YYYYMMDD_HHMMSS.csv`
- `nichos_web_analisis_YYYYMMDD_HHMMSS.parquet`

## 📊 Columnas de Output

| Columna | Descripción |
|---------|-------------|
| `keyword` | La keyword analizada |
| `search_volume` | Volumen de búsqueda mensual estimado |
| `cpc` | Costo por clic promedio (USD) |
| `competition_index` | Índice de competencia (0.0-1.0) |
| `trend_score` | Score de tendencia (-1.0 a 1.0) |
| `decision` | Recomendación automática |

## 🎯 Interpretación de Resultados

### Decisiones:
- **EXCELENTE**: Alto volumen, bajo CPC, baja competencia
- **BUENA**: Buen volumen y CPC razonable
- **ACEPTABLE**: Oportunidad moderada
- **OBSERVAR**: Potencial con tendencia positiva
- **MODERADA**: Revisar otros factores
- **CONSIDERAR**: Revisar manualmente
- **DESCARTAR**: Baja oportunidad

### Trend Score:
- **> 0.1**: Tendencia positiva
- **-0.1 a 0.1**: Tendencia estable
- **< -0.1**: Tendencia negativa

## ⚙️ Configuración

### Archivo seeds_web.txt
- Una keyword por línea
- Líneas que empiecen con `#` son comentarios
- Keywords vacías son ignoradas

### Logging
Los logs se guardan en `nichos_web.log` con información detallada del proceso.

## 🔧 Dependencias

- `pandas`: Manipulación de datos
- `pytrends`: API de Google Trends
- `pyarrow`: Exportación a Parquet
- `requests`: HTTP requests
- `openpyxl`: Soporte Excel

## 📈 Limitaciones Actuales

- Google Ads API no implementada (datos simulados)
- Solo análisis de keywords individuales (no expansión)
- Sin análisis de competencia SERP

## 🛠️ Desarrollo Futuro

- [ ] Integración completa con Google Ads API
- [ ] Expansión automática de keywords relacionadas
- [ ] Análisis de competencia SERP
- [ ] Dashboard web para visualización
- [ ] API REST para integración

## 📄 Licencia

Este proyecto es de uso personal. Revisa las políticas de uso de las APIs de Google antes de usar en producción.

## 🤝 Contribución

Para mejoras o correcciones, por favor crea un issue o pull request.
