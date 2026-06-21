# 🇪🇸 Spain's Migratory Flow

**Trabajo Fin de Grado (TFG)** — Análisis multidimensional de flujos migratorios en España

## 📋 Descripción Ejecutiva

Este proyecto es una **plataforma completa de recolección, procesamiento y análisis de datos** diseñada para estudiar los **flujos migratorios internos y externos en España**. 

Integra datos públicos de múltiples fuentes (AEMET, INE, CNMC, SETID, WAQI, Idealista) para investigar cómo factores **ambientales, económicos, de conectividad y demográficos** influyen en los movimientos de población en España a nivel provincial.

**¿Qué hace este proyecto?**
- ✅ Recopila automáticamente datos de 6+ fuentes públicas y privadas
- ✅ Procesa y limpia datos de forma reproducible
- ✅ Genera visualizaciones y estadísticas descriptivas
- ✅ Ejecuta análisis estadísticos avanzados (correlación, regresión, análisis de género)
- ✅ Produce un dataset maestro unificado para análisis posterior

---

## 🎯 Contexto del Proyecto

Este es un **Trabajo Fin de Grado (TFG)** que busca responder:
> *¿Cómo se relacionan los factores ambientales, económicos y de conectividad con los movimientos migratorios en España?*

El proyecto automatiza completamente el pipeline ETL (Extract-Transform-Load) para permitir:
- Reproducibilidad total de resultados
- Actualización automática de datos
- Análisis exploratorio y estadístico integrado
- Extensibilidad a nuevas fuentes de datos

---

## 🚀 Inicio Rápido (Quick Start)

### Requisitos Previos
- Python 3.10+ (recomendado 3.11)
- Git
- pip

### Instalación (5 minutos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/danielbolanosuax/TFG_Spain-s_Migratory_Flow.git
cd TFG_Spain-s_Migratory_Flow

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (ver sección Configuración)
cp .env.example .env  # Ajustar con tus API keys
```

### Ejecutar el Pipeline

```bash
# Opción 1: Solo recolectar datos (diariamente)
python scheduler.py

# Opción 2: Procesar y analizar datos recolectados
python trigger.py

# Opción 3: Solo ejecutar análisis estadístico avanzado
python run_insights.py
```

---

## 📁 Estructura del Proyecto

### Árbol de Directorios

```
TFG_Spain-s_Migratory_Flow/
├── 📄 README.md                          # Este archivo
├── 📄 requirements.txt                   # Dependencias Python
├── 📄 scheduler.py                       # Recolector automático diario
├── 📄 trigger.py                         # Orquestador del pipeline de análisis
├── 📄 run_insights.py                    # Ejecutor de análisis estadístico
├── 📄 .env                               # Variables de entorno (no versionado)
│
├── 📁 collectors/                        # Módulos de extracción de datos
│   ├── ambiental.py                      # AEMET + WAQI
│   ├── economico.py                      # INE + datos económicos
│   ├── conectividad.py                   # SETID + CNMC
│   ├── evr.py                            # INE EVR (flujos migratorios)
│   └── idealista.py                      # Precios de vivienda
│
├── 📁 notebooks/                         # Pipeline de análisis (Jupyter)
│   ├── 01_exploracion/                   # Exploración inicial de datos crudos
│   ├── 02_limpieza/                      # Limpieza y transformación
│   ├── 03_visualizacion/                 # Visualizaciones exploratorias
│   ├── 04_merge/                         # Consolidación en dataset maestro
│   └── 05_insights/                      # Análisis estadístico avanzado
│
├── 📁 data/                              # Datos recolectados (crudos)
│   ├── ambiental/                        # Por año/mes
│   ├── economico/
│   ├── conectividad/
│   ├── evr/
│   ├── idealista/
│   └── renta_ine/                        # Datos INE históricos
│
└── 📁 output/                            # Resultados y salidas
    ├── 05_descriptivo/                   # Análisis descriptivo
    ├── 06_correlacion/                   # Matrices de correlación
    ├── 07_regresion/                     # Resultados regresiones
    ├── 08_visualizaciones_finales/       # Gráficos finales
    ├── 09_analisis_genero/               # Análisis por género
    ├── merged/                           # Dataset maestro consolidado
    ├── executed_notebooks/               # Notebooks renderizados
    └── logs/                             # Registros de ejecución
```

---

## ⚙️ Configuración Detallada

### Paso 1: Configurar Variables de Entorno

Este proyecto requiere acceso a APIs externas. Crea un archivo `.env` en la raíz con tus credenciales:

```ini
# APIs Públicas (gratuitas)
AEMET_API_KEY=tu_clave_aemet_aqui
WAQI_TOKEN=tu_token_waqi_aqui

# API Idealista (requiere registro)
IDEALISTA_API_KEY=tu_clave_idealista_aqui
IDEALISTA_SECRET=tu_secret_idealista_aqui

# Opcional: Otras configuraciones
LOG_LEVEL=INFO
```

#### Obtener las claves:

| Fuente | URL | Tipo | Costo |
|--------|-----|------|-------|
| **AEMET** | https://www.aemet.es/es/datos_abiertos/AEMET_OpenData | Registro gratuito | Gratis |
| **WAQI** | https://waqi.info/api | Registro gratuito | Gratis (limitado) |
| **Idealista** | https://api.idealista.com/manage | Solicitud comercial | De pago |
| **INE/CNMC/SETID** | API pública (sin key) | Datos abiertos | Gratis |

> ⚠️ **Importante**: Nunca subas el archivo `.env` a GitHub. Está incluido en `.gitignore`.

### Paso 2: Verificar Instalación

```bash
# Probar conectividad AEMET
python test_aemet.py

# Probar Idealista (si tienes credenciales)
python test_idealista.py
```

---

## 🔄 Flujo de Ejecución

El proyecto implementa un **pipeline automático ETL** con 3 fases:

### Fase 1️⃣: Recolección de Datos (`scheduler.py`)

Se ejecuta automáticamente cada día a las 07:00 (hora de Madrid).

```bash
python scheduler.py
```

**Fuentes recolectadas:**
- 🌡️ **Ambiental**: AEMET (observaciones meteorológicas) + WAQI (calidad del aire)
- 💰 **Económico**: INE (mercado laboral, vivienda, renta, turismo, educación)
- 🌐 **Conectividad**: SETID (banda ancha) + CNMC (telecomunicaciones)
- 📊 **Migratorio (EVR)**: INE (flujos y saldos migratorios por provincia)
- 🏠 **Vivienda**: Idealista (precios, con límite de 100 requests/mes)

**Salida**: Archivos JSON organizados por año/mes en la carpeta `data/`

```
data/
├── ambiental/2026/01/20260121.json
├── economico/2026/01/20260121.json
├── conectividad/2026/01/20260121.json
├── evr/2026/01/20260121.json
└── idealista/2026/01/20260121.json
```

### Fase 2️⃣: Procesamiento y Análisis (`trigger.py`)

Ejecuta un pipeline de Jupyter notebooks en orden secuencial:

```bash
python trigger.py
```

**Orden de ejecución:**

| # | Etapa | Notebooks | Descripción |
|----|-------|-----------|-------------|
| 1 | **Exploración** | `01_exploracion/*` | Análisis inicial de datos crudos |
| 2 | **Limpieza** | `02_limpieza/*` | Manejo de valores faltantes, outliers |
| 3 | **Visualización** | `03_visualizacion/*` | Gráficos exploratorios por dominio |
| 4 | **Consolidación** | `04_merge/04_merge.ipynb` | Merge de dominios en dataset maestro |
| 5 | **Análisis Avanzado** | `05_insights/*` (ver siguiente) | Estadísticas y regresiones |

**Salida**: Dataset maestro en `output/merged/master_provincia_anio.csv`

### Fase 3️⃣: Análisis Estadístico (`run_insights.py`)

Ejecuta análisis econométricos y visualizaciones finales:

```bash
python run_insights.py
```

**Análisis realizados:**

- 📈 **Análisis Descriptivo**: Estadísticas básicas y distribuciones
- 📊 **Correlación**: Matrices de correlación entre variables
- 📉 **Regresión**: Modelos econométricos (OLS, fixed effects, etc.)
- 🎨 **Visualizaciones Finales**: Gráficos de resultados principales
- 👫 **Análisis de Género**: Comparación de patrones migratorios por sexo

**Salida**: Resultados en `output/05_descriptivo/`, `output/06_correlacion/`, etc.

---

## 📊 Fuentes de Datos Detalladas

### 🌡️ Ambiental (`collectors/ambiental.py`)

**Propósito**: Recopilar condiciones meteorológicas y calidad del aire

| Fuente | Datos | Cobertura |
|--------|-------|-----------|
| **AEMET OpenData** | Temperatura, precipitación, presión, viento | Nacional (estaciones) |
| **WAQI** | Índice de calidad del aire (PM2.5, PM10, O3, NO2) | Ciudades principales |

### 💰 Económico (`collectors/economico.py`)

**Propósito**: Indicadores socioeconómicos y mercado laboral

| Fuente | Datos | Nivel |
|--------|-------|-------|
| **INE** | Empleo, renta, vivienda, educación, turismo | Provincial |
| **MIVAU** | Precios de alquiler de referencia | Municipal |
| **Min. Sanidad** | Distribución de centros sanitarios | Municipal |
| **Min. Interior** | Tasa de criminalidad (metadatos) | Provincial |
| **Catastro** | Servicios e infraestructuras | Municipal |

### 🌐 Conectividad (`collectors/conectividad.py`)

**Propósito**: Infraestructura de comunicaciones

| Fuente | Datos | Cobertura |
|--------|-------|-----------|
| **SETID** | Cobertura de banda ancha | Municipal |
| **CNMC** | Calidad de telecomunicaciones | Provincial |

### 📊 Migratorio - EVR (`collectors/evr.py`)

**Propósito**: Flujos y saldos migratorios

**Series del INE:**
- Flujos interprovinciales (origen → destino) por sexo
- Saldo migratorio por provincia, sexo y edad
- Perfil demográfico de migrantes (edad, sexo)

### 🏠 Vivienda - Idealista (`collectors/idealista.py`)

**Propósito**: Datos de oferta y precios inmobiliarios

**Características:**
- Precios de venta y alquiler por ubicación
- Características de inmuebles (m², habitaciones, etc.)
- ⚠️ **Limitación crítica**: 100 peticiones/mes máximo
- 20 peticiones de buffer de seguridad
- Modo `dry_run` para pruebas sin consumir cuota

---

## 📊 Fuentes de Datos Detalladas

### 🌡️ Ambiental (`collectors/ambiental.py`)

**Propósito**: Recopilar condiciones meteorológicas y calidad del aire

| Fuente | Datos | Cobertura |
|--------|-------|-----------|
| **AEMET OpenData** | Temperatura, precipitación, presión, viento | Nacional (estaciones) |
| **WAQI** | Índice de calidad del aire (PM2.5, PM10, O3, NO2) | Ciudades principales |

### 💰 Económico (`collectors/economico.py`)

**Propósito**: Indicadores socioeconómicos y mercado laboral

| Fuente | Datos | Nivel |
|--------|-------|-------|
| **INE** | Empleo, renta, vivienda, educación, turismo | Provincial |
| **MIVAU** | Precios de alquiler de referencia | Municipal |
| **Min. Sanidad** | Distribución de centros sanitarios | Municipal |
| **Min. Interior** | Tasa de criminalidad (metadatos) | Provincial |
| **Catastro** | Servicios e infraestructuras | Municipal |

### 🌐 Conectividad (`collectors/conectividad.py`)

**Propósito**: Infraestructura de comunicaciones

| Fuente | Datos | Cobertura |
|--------|-------|-----------|
| **SETID** | Cobertura de banda ancha | Municipal |
| **CNMC** | Calidad de telecomunicaciones | Provincial |

### 📊 Migratorio - EVR (`collectors/evr.py`)

**Propósito**: Flujos y saldos migratorios

**Series del INE:**
- Flujos interprovinciales (origen → destino) por sexo
- Saldo migratorio por provincia, sexo y edad
- Perfil demográfico de migrantes (edad, sexo)

### 🏠 Vivienda - Idealista (`collectors/idealista.py`)

**Propósito**: Datos de oferta y precios inmobiliarios

**Características:**
- Precios de venta y alquiler por ubicación
- Características de inmuebles (m², habitaciones, etc.)
- ⚠️ **Limitación crítica**: 100 peticiones/mes máximo
- 20 peticiones de buffer de seguridad
- Modo `dry_run` para pruebas sin consumir cuota

---

## 📚 Estructura de Notebooks

### `01_exploracion/` — Exploración Inicial
Carga y visualiza datos crudos para entender su estructura, valores faltantes y distribuciones.

**Notebooks:**
- `01_ambiental.ipynb` — Análisis de series meteorológicas
- `01_conectividad.ipynb` — Cobertura de banda ancha y telecomunicaciones
- `01_economico.ipynb` — Indicadores económicos y laborales
- `01_evr.ipynb` — Flujos y saldos migratorios
- `01_idealista.ipynb` — Oferta inmobiliaria

### `02_limpieza/` — Limpieza y Transformación
Maneja valores faltantes, outliers, duplicados y transforma datos al formato estándar.

**Proceso:**
- Identificar y imputar valores NaN
- Detectar y tratar outliers
- Normalizar variables
- Crear variables derivadas

### `03_visualizacion/` — Visualización Exploratoria
Genera gráficos para explorar relaciones entre variables y anomalías.

**Gráficos:** Histogramas, boxplots, scatter plots, series temporales

### `04_merge/` — Consolidación de Dominios
Integra todos los dominios en un único dataset maestro organizadopor provincia y año.

**Output:** `output/merged/master_provincia_anio.csv`

### `05_insights/` — Análisis Estadístico Avanzado

Ejecutado con `papermill` para reproducibilidad total:

- `05_analisis_descriptivo.ipynb` — Estadísticas principales
- `06_correlacion.ipynb` — Matrices y gráficos de correlación
- `07_regresion.ipynb` — Modelos econométricos (OLS, efectos fijos, etc.)
- `08_visualizaciones_finales.ipynb` — Gráficos de publicación
- `09_analisis_genero.ipynb` — Análisis diferenciado por sexo

---

## 📈 Dependencias Python

Las librerías clave utilizadas (todas incluidas en `requirements.txt`):

| Librería | Versión | Propósito |
|----------|---------|----------|
| `pandas` | - | Manipulación y análisis de datos |
| `numpy` | - | Computación numérica |
| `requests` | - | Llamadas HTTP a APIs |
| `python-dotenv` | - | Carga de variables `.env` |
| `matplotlib` | - | Visualizaciones básicas |
| `seaborn` | - | Visualizaciones estadísticas |
| `papermill` | - | Ejecución automática de notebooks |
| `scipy` | - | Funciones estadísticas |
| `statsmodels` | - | Modelos econométricos |
| `scikit-learn` | - | Machine learning |
| `linearmodels` | - | Modelos de panel data |
| `duckdb` | - | Queries SQL en memoria |
| `APScheduler` | - | Planificación de tareas |

---

## 📊 Resultados y Salidas

### Dataset Maestro

**Archivo**: `output/merged/master_provincia_anio.csv`

Tabla consolidada con todas las variables de los 5 dominios:

| Columna Ejemplo | Tipo | Descripción |
|-----------------|------|-------------|
| `provincia` | string | Nombre de provincia |
| `year` | int | Año de observación |
| `temp_media` | float | Temperatura media (AEMET) |
| `tasa_empleo` | float | Tasa de empleo (INE) |
| `cobertura_adsl` | float | % cobertura banda ancha (SETID) |
| `saldo_migratorio` | float | Saldo migratorio neto (EVR) |
| ... | - | +50 variables adicionales |

### Análisis y Visualizaciones

**Ubicación**: `output/`

```
output/
├── 05_descriptivo/          # Estadísticas descriptivas por variable
│   ├── figs/                # Gráficos
│   └── tables/              # Tablas resumidas (CSV, Excel)
│
├── 06_correlacion/          # Matrices de correlación
│   ├── figs/                # Heatmaps, gráficos de correlación
│   └── tables/
│
├── 07_regresion/            # Modelos econométricos
│   ├── figs/                # Residuales, efectos, etc.
│   └── tables/              # Coeficientes, p-valores, R²
│
├── 08_visualizaciones_finales/  # Gráficos de publicación
│   └── figs/
│
├── 09_analisis_genero/      # Análisis diferenciado por sexo
│   ├── figs/
│   └── tables/
│
└── executed_notebooks/      # Notebooks (.ipynb) con outputs renderizados
```

### Logs y Auditoría

- `output/logs/` — Registros de ejecución (timestamps, errores)
- `data/idealista_requests_log.json` — Control de peticiones a Idealista

---

## 🧪 Verificación de Instalación

Después de configurar `.env`, prueba la conectividad a las APIs:

```bash
# Probar AEMET (API pública, no requiere key en muchos casos)
python test_aemet.py

# Probar Idealista (requiere API key)
python test_idealista.py
```

---

## ⚠️ Limitaciones y Consideraciones

| Limitación | Detalles | Impacto |
|-----------|---------|--------|
| **Idealista** | Máx. 100 peticiones/mes | Requiere planificación cuidadosa |
| **CNMC** | Sin API pública estable | Descarga manual recomendada |
| **AEMET** | Rate limiting | Agregar retrasos si es necesario |
| **Historico EVR** | Datos limitados a años recientes | Serie temporal corta |
| **Sin Dashboard** | No hay interfaz web interactiva | Análisis por notebooks/CSV |

---

## 💡 Buenas Prácticas

### Orden de Ejecución Recomendado

```bash
# 1️⃣ Recolectar datos nuevos
python scheduler.py

# 2️⃣ Procesar: exploración → limpieza → visualización → merge
python trigger.py

# 3️⃣ Análisis estadístico final
python run_insights.py
```

### Seguridad

- ✅ **Nunca** commites el archivo `.env` a Git
- ✅ Almacena API keys en variables de entorno, no en el código
- ✅ Usa `.env.example` como plantilla de referencia
- ✅ Rota credenciales regularmente

### Reproducibilidad

- ✅ Usa `APScheduler` para automatizar recolección
- ✅ Los notebooks usan `papermill` para ejecución determinista
- ✅ Seeds de aleatoriedad fijados en análisis
- ✅ Versions de paquetes congeladas en `requirements.txt`

---

## 🚀 Próximos Pasos (Roadmap)

- [ ] Integración con PostgreSQL para series temporales
- [ ] Descarga automática de datos CNMC via API alternativa
- [ ] Análisis espacial con shapefiles (mapa de correlaciones)
- [ ] Dashboard interactivo en Streamlit/Plotly
- [ ] Exportación automática de informes PDF
- [ ] CI/CD pipeline con GitHub Actions
- [ ] Tests unitarios para collectors

---

## 📞 Contacto y Contribuciones

**Autor**: Proyecto de Grado, Universitat Autònoma de Barcelona

**Licencia**: Investigación académica - respeta los TOS de cada fuente de datos

### Fuentes de Datos y Licencias

- **AEMET**: [OpenData License](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData)
- **INE**: [CC BY 4.0](https://www.ine.es/)
- **WAQI**: [Términos de Servicio](https://waqi.info/about-us/)
- **CNMC/SETID**: Datos abiertos españoles
- **Idealista**: Licencia comercial (requiere acuerdo)

---

## ❓ FAQ - Preguntas Frecuentes

**P: ¿Cuánto tiempo tarda ejecutar todo el pipeline?**
R: Aproximadamente 30-60 minutos (depende de conexión y recursos)

**P: ¿Puedo usar solo algunos collectors?**
R: Sí, cada collector es independiente. Comenta el que no necesites en `scheduler.py`

**P: ¿Qué pasa si falla una descarga?**
R: Los collectors implementan reintentos y logging. Revisa `output/logs/` para detalles

**P: ¿Puedo extender con nuevas fuentes de datos?**
R: Sí, crea un nuevo archivo en `collectors/` siguiendo el patrón de los existentes

**P: ¿Dónde guarda los datos?**
R: Todo en `data/` (raw) y `output/` (procesados). No usa base de datos actualmente

---

**Última actualización**: Junio 2026  
**Estado**: Proyecto Activo

