# 🚀 Proyecto 201 digital - Sistema Automatizado de Nichos Rentables

**Versión 1.0 - Opción A: Sistema automático con límites diarios**

Automatización completa para encontrar nichos rentables en YouTube usando Google Trends y YouTube Data API.

## 🎯 **SISTEMA COMPLETO FUNCIONANDO** ✅

### Resultados del Primer Análisis:
- **12 nichos analizados** exitosamente
- **24 requests a YouTube API** (dentro de límites)
- **Top nicho**: "criptomonedas para principiantes" (Score: 0.648)
- **Tiempo de ejecución**: ~25 segundos

### Comandos para Usar el Sistema:

```bash
# 🧪 Verificar que todo funciona
python scripts/test_system.py

# � Análisis completo (con Google Trends cuando esté disponible)
python scripts/niche_analyzer.py

# 🎯 Análisis básico funcional (recomendado por ahora)
python scripts/niche_analyzer_basic.py

# 📊 Análisis individual de nichos
python scripts/youtube_search.py
```

## 🎯 Flujo Optimizado Implementado

```
🔥 Google Trends → 🎯 Filtrado Inteligente → 📊 YouTube Validation → 🏆 Opportunity Score
```

### Por qué este flujo es eficiente:
- **Google Trends**: Gratis, sin límites estrictos, identifica tendencias actuales
- **Filtrado**: Reduce consultas a YouTube API (cuota limitada: 10,000 unidades/día)
- **YouTube Validation**: Datos reales de competencia y potencial
- **Scoring**: Algoritmo que calcula oportunidad de monetización

## 📁 Estructura del Proyecto

```
Proyecto 201 digital/
├── scripts/
│   ├── niche_analyzer.py         # 🚀 SCRIPT PRINCIPAL - Sistema completo
│   ├── niche_analyzer_basic.py   # 🎯 SCRIPT FUNCIONAL - Sin Trends
│   ├── youtube_search.py         # 📊 Análisis YouTube individual
│   ├── test_system.py           # 🧪 Verificación del sistema
│   ├── google_ads_keywords.py    # 💰 Google Ads (pendiente)
│   └── obtener_refresh_token.py
├── credentials/
│   ├── config.py                # ⚙️ Configuración centralizada
│   ├── google-ads.yaml          # 🔑 Google Ads (pendiente)
│   └── cliente_oauth.json       # 🔐 OAuth credentials
├── docs/                        # 📚 Documentación
│   └── ejemplo_resultados.md    # 📊 Ejemplo de resultados
├── requirements.txt             # 📦 Dependencias
├── install.py                  # 🔧 Instalador automático
└── README.md                   # 📖 Este archivo
```

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendado)
```bash
python install.py
```

### Opción 2: Instalación Manual
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import pytrends; from googleapiclient.discovery import build; print('✅ Todo instalado')"
```

## ⚙️ Configuración

### 1. Verificar API Key de YouTube
Edita `credentials/config.py`:
```python
YOUTUBE_API_KEY = "tu_api_key_aqui"
```

### 2. Ejecutar Sistema Automatizado
```bash
python scripts/niche_analyzer_basic.py
```

## 📊 Resultados y Reportes

El sistema genera un reporte completo con:
- 🏆 Top 5 nichos recomendados
- 📈 Opportunity Score de cada nicho
- 👥 Nivel de competencia
- 💰 Potencial de monetización
- 🎬 Estadísticas de videos

## 🔢 Límites de API (Opción A)

| API | Límite Diario | Uso en Sistema |
|-----|---------------|----------------|
| Google Trends | ~50 requests | Análisis de tendencias |
| YouTube Data API | 10,000 unidades | Validación de nichos |
| **Total diario** | ~100 requests | Análisis completo |

## 💡 Comandos Útiles

```bash
# 🧪 Probar sistema antes de usar
python scripts/test_system.py

# 🚀 Análisis completo automatizado
python scripts/niche_analyzer.py

# 🎯 Análisis básico funcional (recomendado)
python scripts/niche_analyzer_basic.py

# 📊 Análisis individual de YouTube
python scripts/youtube_search.py

# 📖 Ver documentación completa
type README.md

# 📋 Ver ejemplo de resultados
type docs\ejemplo_resultados.md
```

### 2. Ejecutar Sistema Automatizado
```bash
python scripts/niche_analyzer.py
```

## 🎯 Cómo Funciona el Sistema

### Fase 1: Google Trends Analysis
- Obtiene tendencias actuales del día
- Busca keywords relacionadas con potencial
- Filtra automáticamente las más prometedoras

### Fase 2: YouTube Validation
- Valida keywords con datos reales de YouTube
- Analiza competencia y views promedio
- Calcula nivel de saturación del nicho

### Fase 3: Opportunity Scoring
- **Trends Score** (30%): Popularidad en búsquedas
- **Competition Score** (25%): Nivel de competencia
- **Monetization Potential** (25%): Potencial de ingresos
- **Growth Potential** (20%): Capacidad de crecimiento

## 📊 Resultados y Reportes

El sistema genera un reporte completo con:
- 🏆 Top 5 nichos recomendados
- 📈 Opportunity Score de cada nicho
- 👥 Nivel de competencia
- 💰 Potencial de monetización
- 🎬 Estadísticas de videos

## 🔢 Límites de API (Opción A)

| API | Límite Diario | Uso en Sistema |
|-----|---------------|----------------|
| Google Trends | ~50 requests | Análisis de tendencias |
| YouTube Data API | 10,000 unidades | Validación de nichos |
| **Total diario** | ~100 requests | Análisis completo |

## � Comandos Útiles

```bash
# Análisis completo automatizado
python scripts/niche_analyzer.py

# Análisis individual de YouTube
python scripts/youtube_search.py

# Instalar dependencias
python install.py

# Ver documentación completa
cat README.md
```

## 🔒 Seguridad y Credenciales

- ✅ API Keys en `credentials/config.py`
- ✅ Nunca subir credenciales a Git
- ✅ Backup seguro de carpeta `credentials/`
- ✅ Configuración centralizada

## 📈 APIs Configuradas

| API | Estado | Uso |
|-----|--------|-----|
| ✅ YouTube Data API v3 | Configurada | Análisis de nichos |
| ✅ Google Trends | Listo | Tendencias de búsqueda |
| 🔄 Google Ads API | Pendiente aprobación | Keywords comerciales |

## 🎯 Próximos Pasos

1. **Ejecutar primer análisis**: `python scripts/niche_analyzer.py`
2. **Revisar resultados** y seleccionar nicho principal
3. **Crear contenido** basado en recomendaciones
4. **Monitorear rendimiento** y ajustar estrategia

## 📞 Soporte

- 📧 Documentación completa en carpeta `docs/`
- 🔧 Scripts optimizados para estabilidad
- 📊 Reportes detallados de cada análisis

---
**Proyecto 201 digital** - Encontrando nichos rentables automáticamente
**Fecha**: 28/08/2025 | **Versión**: 1.0
