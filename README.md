# 🇪🇸 Spain's Migratory Flow

## Descripción

Este proyecto es una plataforma de recolección, procesamiento y análisis de datos dedicada a estudiar los flujos migratorios en España. Combina múltiples dominios de datos públicos para construir un conjunto de trabajo reproducible que permita explorar cómo factores ambientales, económicos y de conectividad se relacionan con los movimientos internos y externos de población.

El código implementado incluye:
- Colección automatizada de datos de AEMET, WAQI, INE, SETID, CNMC y EVR.
- Control de límite mensual para el collector de Idealista.
- Un `scheduler` diario que descarga datos y los guarda en carpetas organizadas por año/mes.
- Un `trigger` de análisis que ejecuta notebooks secuenciales para exploración, limpieza, visualización y merge.
- Ejecución de notebooks de análisis avanzado (`05_insights`) con `papermill`.

> Nota: la configuración actual guarda metadatos y resultados en JSON y carpetas de salida, pero no incluye un servicio web ni dashboards interactivos en la implementación actual.

---

## Contenido principal

- `scheduler.py` — orquestador de colecciones diarias
- `trigger.py` — orquestador de notebooks de análisis
- `run_insights.py` — runner dedicado a notebooks de insights
- `test_aemet.py` — prueba de conectividad AEMET
- `test_idealista.py` — pruebas de integración Idealista
- `collectors/` — módulos de extracción de datos
- `notebooks/` — flujos de análisis exploratorio, limpieza, visualización y consolidación
- `data/` — datos recolectados en bruto
- `output/` — resultados, visualizaciones y notebooks ejecutados
- `config/endpoints.yaml` — placeholder de configuración (vacío actualmente)

---

## Requisitos

- Python 3.8+ (recomendado 3.10/3.11)
- `pip`
- `git`
- Paquetes listados en `requirements.txt`

### Dependencias clave reales

- `requests` — llamadas HTTP a APIs públicas
- `python-dotenv` — carga variables de entorno desde `.env`
- `pandas`, `numpy` — procesamiento de datos
- `matplotlib`, `seaborn` — visualización
- `papermill` — ejecución automática de notebooks
- `scipy`, `statsmodels`, `scikit-learn`, `linearmodels` — análisis estadístico y modelos econométricos
- `duckdb` — consultas y procesamiento eficiente en memoria
- `APScheduler` — planificación de ejecución diaria

---

## Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/danielbolanosuax/TFG_Spain-s_Migratory_Flow.git
cd TFG_Spain-s_Migratory_Flow
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear `.env`

Este proyecto carga variables desde un fichero `.env` en la raíz del repositorio.

Ejemplo mínimo:

```ini
AEMET_API_KEY=tu_api_key_aemet
WAQI_TOKEN=tu_token_waqi
IDEALISTA_API_KEY=tu_api_key_idealista
IDEALISTA_SECRET=tu_secret_idealista
```

### 5. Variables soportadas

- `AEMET_API_KEY` — clave para AEMET OpenData
- `WAQI_TOKEN` — token para WAQI
- `IDEALISTA_API_KEY` — clave para Idealista API
- `IDEALISTA_SECRET` — secreto para Idealista API

> En este repositorio existe un `.env` local con valores de ejemplo; no debería incluirse en producción ni en un repositorio público.

---

## Flujo de ejecución actual

### 1. Recolección diaria de datos

El archivo `scheduler.py` ejecuta la colección de estos dominios:
- `collectors.economico` — datos de INE y otras fuentes nacionales
- `collectors.ambiental` — observación AEMET y calidad de aire WAQI
- `collectors.conectividad` — cobertura SETID y metadatos CNMC
- `collectors.evr` — flujos y saldos de migración de INE

```bash
python scheduler.py
```

Esto guarda archivos JSON en:

- `data/economico/<año>/<mes>/<fecha>.json`
- `data/ambiental/<año>/<mes>/<fecha>.json`
- `data/conectividad/<año>/<mes>/<fecha>.json`
- `data/evr/<año>/<mes>/<fecha>.json`

El scheduler también programa la ejecución diaria a las 07:00 hora de Madrid.

### 2. Ejecución de análisis integrado

El archivo `trigger.py` está diseñado para ejecutar un pipeline de notebooks en este orden:

1. `notebooks/01_exploracion/*`
2. `notebooks/02_limpieza/*`
3. `notebooks/03_visualizacion/*`
4. `notebooks/04_merge/04_merge.ipynb`
5. `run_insights.py` → `notebooks/05_insights/*`

```bash
python trigger.py
```

> Nota de implementación actual: `trigger.py` intenta usar una función llamada `run_scheduler_once()` en el paso de colección, pero ese nombre no está definido en el archivo. La colección principal está implementada en `run_coleccion()`, por lo que el script requiere ajustar ese detalle para funcionar sin error.

### 3. Ejecución de insights

Para ejecutar únicamente los notebooks de análisis estadístico y visualizaciones finales:

```bash
python run_insights.py
```

Esto genera notebooks renderizados en:

- `output/executed_notebooks/`

---

## Colecciones implementadas

### `collectors/ambiental.py`

Recoge:
- observación convencional completa de AEMET (`AEMET OpenData`)
- calidad del aire WAQI para ciudades españolas

### `collectors/economico.py`

Recoge:
- varias tablas INE de mercado laboral, vivienda, renta, turismo, educación y densidad de población
- datos de crimen del Ministerio del Interior (metadatos)
- catálogo de centros de salud del Ministerio de Sanidad
- datos de referencia de precio de alquiler desde MIVAU
- servicios del Catastro para municipios seleccionados

### `collectors/conectividad.py`

Recoge:
- metadatos de cobertura de banda ancha SETID
- metadatos de calidad de telecomunicaciones CNMC (descarga manual)

### `collectors/evr.py`

Recoge series de migración del INE:
- flujo interprovincial por año, sexo y provincia de origen/destino
- saldo migratorio por provincia, sexo y edad
- perfil demográfico por edad y sexo

### `collectors/idealista.py`

Implementa un collector de precios de vivienda con la API de Idealista. Tiene restricciones críticas de uso:
- límite mensual de `100` peticiones
- buffer de seguridad de `20` peticiones
- modo `dry_run` para pruebas sin consumir cuota

> El collector de Idealista está incluido en `trigger.py`, pero no forma parte de `scheduler.py` en la implementación actual.

---

## Estructura del repositorio

```
TFG_Spain-s_Migratory_Flow/
├── README.md
├── requirements.txt
├── .env
├── scheduler.py
├── trigger.py
├── run_insights.py
├── test_aemet.py
├── test_idealista.py
├── fix_chdir.py
├── config/
│   └── endpoints.yaml
├── collectors/
│   ├── __init__.py
│   ├── ambiental.py
│   ├── economico.py
│   ├── conectividad.py
│   ├── evr.py
│   ├── idealista.py
├── notebooks/
│   ├── 01_exploracion/
│   ├── 02_limpieza/
│   ├── 03_visualizacion/
│   ├── 04_merge/
│   └── 05_insights/
├── data/
│   ├── ambiental/
│   ├── economico/
│   ├── conectividad/
│   ├── evr/
│   └── idealista_requests_log.json
└── output/
    ├── ambiental/
    ├── conectividad/
    ├── economico/
    ├── evr/
    ├── idealista/
    ├── merged/
    ├── executed_notebooks/
    └── logs/
```

---

## Notebooks y análisis

### 01_exploracion
Explora los datos crudos recolectados. Incluye notebooks para cada dominio y un notebook para Idealista.

### 02_limpieza
Limpia y transforma datos crudos para que estén listos para análisis.

### 03_visualizacion
Genera visualizaciones de los conjuntos de datos limpios por dominio.

### 04_merge
Consolida los dominios en un dataset maestro unificado.

### 05_insights
Contiene análisis avanzados y resultados finales:
- análisis descriptivo
- correlación
- regresión
- visualizaciones finales
- análisis de género

---

## Resultados esperados

### Salidas principales

- `output/merged/master_provincia_anio.csv` — dataset maestro consolidado
- `output/executed_notebooks/` — notebooks con resultados renderizados
- `output/logs/` — registros de ejecución
- `output/05_descriptivo/`, `06_correlacion/`, `07_regresion/`, `08_visualizaciones_finales/`, `09_analisis_genero/` — resultados de análisis por fase

### Otros resultados

- `output/idealista/` — datos y visualizaciones específicas de Idealista
- `data/idealista_requests_log.json` — control de peticiones Idealista

---

## Pruebas y diagnóstico

### AEMET

```bash
python test_aemet.py
```

### Idealista

```bash
python test_idealista.py
```

---

## Limitaciones actuales

- `config/endpoints.yaml` existe como placeholder y está vacío actualmente.
- `trigger.py` referencia una función no definida (`run_scheduler_once`) durante la fase de colección.
- CNMC no ofrece API pública estable; la implementación actual solo registra metadatos y sugiere descarga manual.
- El collector de Idealista está sujeto a límite mensual estricto y debe usarse con cuidado.
- No existe un servidor web integrado ni un dashboard interactivo implementado.

---

## Buenas prácticas

- Ejecutar primero `python scheduler.py` para recolectar datos.
- Luego ejecutar `python trigger.py` para procesar y analizar.
- Usar `python run_insights.py` cuando solo se desea reproducir el análisis estadístico.
- Mantener la carpeta `data/` organizada por año y mes.
- Guardar claves sensibles fuera del repositorio.

---

## Extensiones futuras

- Añadir almacenamiento en base de datos para series temporales
- Automatizar la descarga de datos CNMC y SETID
- Incorporar análisis espacial con shapefiles
- Crear dashboards exploratorios en Streamlit o similar
- Exportar informes automáticos en PDF

---

## Licencia

Proyecto de investigación con datos públicos. Respetar las condiciones de uso de cada fuente de datos.

- AEMET: OpenData
- INE: datos públicos nacionales
- CNMC/SETID: datos abiertos
- WAQI: términos de uso del servicio
- Idealista: API privada con límite de uso
