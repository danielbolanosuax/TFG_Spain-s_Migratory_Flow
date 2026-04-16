# 🇪🇸 Spain's Migratory Flow Analysis

**Advanced data collection and analysis platform for understanding Spain's internal and external migration patterns through environmental, economic, and connectivity indicators.**

> A comprehensive framework that systematically integrates multidimensional indicators from authoritative Spanish government data sources to enable research into migration drivers and socioeconomic impacts.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Highlights](#project-highlights)
- [System Architecture](#system-architecture)
- [Installation & Setup](#installation--setup)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Data Collection](#data-collection)
- [Analysis Pipeline](#analysis-pipeline)
- [Results & Outputs](#results--outputs)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This research project provides an integrated framework for studying Spain's migratory dynamics through three interconnected dimensions:

- **🌍 Environmental Indicators**: Weather patterns, air quality, and climate conditions
- **💰 Economic Indicators**: Labor market, income distribution, tourism, and public services
- **📡 Connectivity Indicators**: Broadband coverage and telecommunications quality

The platform automatically collects, processes, and consolidates open data from authoritative Spanish institutions on a daily basis, creating a structured, time-series dataset suitable for statistical analysis, predictive modeling, and evidence-based policy research.

### Key Context

Internal and international migration is shaped by complex interactions between:
- Environmental conditions (climate, natural disasters, air quality)
- Economic opportunities (employment, income, sectoral activity)
- Infrastructure development (broadband, telecom services)
- Public services availability (healthcare, education, safety)

This project systematically quantifies these dimensions at regular intervals, enabling rigorous analysis of migration determinants.

---

## ✨ Project Highlights

✅ **Automated Daily Collection** — Executes comprehensive data pipeline every morning at 07:00 Madrid time  
✅ **Multi-Source Integration** — Aggregates data from 20+ public APIs and data sources  
✅ **Standardized Format** — Normalized JSON structure for seamless analysis  
✅ **Time-Series Design** — Organized by year/month for temporal analysis  
✅ **Full Analytics Stack** — From raw data collection to statistical modeling and visualizations  
✅ **Production-Ready** — Scheduled execution, error handling, and comprehensive logging  

---

## 🏗️ System Architecture

### Core Components

#### 1. **Data Collectors** (`collectors/`)

Three specialized collector modules that extract data from distinct domains:

##### **Environmental Collector** (`ambiental.py`)

Captures meteorological and air quality data from Spain's environmental monitoring network:

- **AEMET Weather Data**
  - Source: Spanish State Meteorological Agency OpenData API
  - Coverage: ~10,000 meteorological stations nationwide
  - Metrics: Temperature, precipitation, humidity, wind (speed/direction), atmospheric pressure, solar radiation
  - Update: Real-time continuous monitoring

- **Air Quality Index (WAQI)**
  - Multi-pollutant monitoring: NO₂, PM₁₀, PM₂.₅, O₃, SO₂, CO
  - Primary focus: Madrid metropolitan region
  - Sources: World Air Quality Index API / Madrid City Council
  - Update frequency: 20-minute intervals

##### **Economic Collector** (`economico.py`)

Aggregates socioeconomic indicators from Spain's National Statistics Institute (INE) and sectoral ministries:

| Indicator | Source | Granularity |
|-----------|--------|-------------|
| Unemployment rates | INE | Autonomous Community (CCAA) |
| Household income | INE | Regional |
| Population density | INE | Municipality |
| Tourism arrivals & stays | Ministry of Industry | Regional |
| Educational centers | Ministry of Education | CCAA |
| Hospital & healthcare catalog | Ministry of Health | National |
| Crime statistics | Ministry of Interior | Regional |

##### **Connectivity Collector** (`conectividad.py`)

Monitors digital infrastructure accessibility and performance:

- **Broadband Coverage (SETID)**
  - Technologies: Fiber, 4G, 5G, HFC, VDSL
  - Granularity: Municipality level
  - Frequency: Semiannual reports
  - Source: State Secretariat for Digitization

- **Telecom Quality (CNMC)**
  - Metrics: Download/upload speeds, network performance
  - Segmentation: By operator and technology
  - Frequency: Quarterly updates
  - Source: National Telecom Commission

##### **Migration Data Collector** (`evr.py`)

Provides official migration flow statistics:
- Stock and flows of internal/external migration
- Segmentation by province and gender
- Source: Spanish National Statistics (EVR registration data)

#### 2. **Orchestration Engine** (`scheduler.py`)

Automated scheduling and execution system with:

- **Daily Pipeline Execution**: Runs all collectors simultaneously at 07:00 Madrid time (CET/CEST)
- **Data Persistence**: Organized directory structure → `data/<category>/<year>/<month>/<DD_MM_YYYY>.json`
- **Format Standardization**: UTF-8 encoded JSON with proper indentation
- **Logging & Monitoring**: Real-time execution feedback and status indicators
- **Blocking Mode**: Continuous operation with indefinite scheduling

#### 3. **Analysis Pipeline** (`trigger.py`, `run_insights.py`)

Orchestrates the complete analysis workflow:

- **Data Merging**: Consolidates collected data across all domains
- **Notebook Execution**: Automated execution of analysis notebooks using Papermill
- **Sequential Processing**: 5 main analysis phases with dependencies
- **Logging**: Comprehensive execution logs for debugging and monitoring

---

## 📁 Project Structure

```
TFG_Spain-s_Migratory_Flow/
│
├── 📄 README.md                          # This documentation
├── 📄 requirements.txt                   # Python dependencies
├── 🔧 config/
│   └── endpoints.yaml                    # API configuration
│
├── 🤖 Automation Scripts
│   ├── scheduler.py                      # Daily job scheduler
│   ├── trigger.py                        # Analysis orchestrator
│   ├── run_insights.py                   # Notebook executor
│   ├── test_aemet.py                     # AEMET connectivity test
│   └── fix_chdir.py                      # Path resolution utility
│
├── 📊 collectors/                        # Data collection modules
│   ├── __init__.py
│   ├── ambiental.py                      # Environmental data
│   ├── economico.py                      # Economic indicators
│   ├── conectividad.py                   # Connectivity metrics
│   └── evr.py                            # Migration flows
│
├── 📓 notebooks/                         # Analysis workflows
│   ├── 01_exploracion/                   # Data exploration
│   │   ├── 01_ambiental.ipynb
│   │   ├── 01_conectividad.ipynb
│   │   ├── 01_economico.ipynb
│   │   └── 01_evr.ipynb
│   │
│   ├── 02_limpieza/                      # Data cleaning & preprocessing
│   │   ├── 02_ambiental.ipynb
│   │   ├── 02_conectividad.ipynb
│   │   ├── 02_economico.ipynb
│   │   └── 02_evr.ipynb
│   │
│   ├── 03_visualizacion/                 # Domain-specific visualizations
│   │   ├── 03_ambiental.ipynb
│   │   ├── 03_conectividad.ipynb
│   │   ├── 03_economico.ipynb
│   │   ├── 03_evr.ipynb
│   │   └── output/
│   │
│   ├── 04_merge/                         # Data consolidation
│   │   ├── 04_merge.ipynb
│   │   └── output/
│   │       └── merged/                   # Consolidated datasets
│   │           └── master_provincia_anio.csv
│   │
│   └── 05_insights/                      # Advanced statistical analysis
│       ├── 05_analisis_descriptivo.ipynb # Descriptive statistics
│       ├── 06_correlacion.ipynb          # Correlation analysis
│       ├── 07_regresion.ipynb            # Regression modeling
│       ├── 08_visualizaciones_finales.ipynb # Publication-ready figures
│       └── 09_analisis_genero.ipynb      # Gender-disaggregated analysis
│
├── 📈 data/                              # Raw collected data (time-series)
│   ├── ambiental/2026/04/
│   ├── economico/2026/04/
│   ├── conectividad/2026/04/
│   └── evr/
│       ├── evr_flujos_provincia_sexo.json
│       └── evr_saldo_provincia_sexo.json
│
├── 📊 output/                            # Analysis results & outputs
│   ├── 05_descriptivo/
│   │   ├── tables/                       # Statistical tables (CSV)
│   │   │   ├── estadisticas_master.csv
│   │   │   ├── impacto_covid_provincia.csv
│   │   │   └── ranking_provincias_saldo_medio.csv
│   │   └── figs/                         # Descriptive plots
│   │
│   ├── 06_correlacion/
│   │   ├── tables/
│   │   │   ├── correlacion_anual.csv
│   │   │   ├── correlacion_por_segmento.csv
│   │   │   ├── matriz_correlacion_pearson.csv
│   │   │   └── resumen_correlaciones.csv
│   │   └── figs/
│   │
│   ├── 07_regresion/
│   │   ├── tables/                       # Model coefficients & diagnostics
│   │   │   ├── coeficientes_comparativa.csv
│   │   │   ├── comparativa_modelos.csv
│   │   │   ├── vif_multicolinealidad.csv
│   │   │   ├── ols_base_summary.txt
│   │   │   ├── ols_extendido_summary.txt
│   │   │   ├── panel_fe_summary.txt
│   │   │   └── resumen_modelos.csv
│   │   └── figs/
│   │
│   ├── 08_visualizaciones_finales/
│   │   └── figs/                         # Publication-quality visualizations
│   │
│   ├── 09_analisis_genero/
│   │   ├── tables/
│   │   │   ├── genero_provincia_anio.csv
│   │   │   └── ranking_feminizacion_provincia.csv
│   │   └── figs/
│   │
│   ├── ambiental/, conectividad/, economico/, evr/
│   │   ├── 01-raw/                       # Processed raw data
│   │   ├── 02-silver/                    # Cleaned datasets
│   │   └── 03-gold/                      # Analysis-ready data
│   │
│   ├── executed_notebooks/               # Notebook execution outputs
│   │   ├── 05_analisis_descriptivo_executed.ipynb
│   │   ├── 06_correlacion_executed.ipynb
│   │   ├── 07_regresion_executed.ipynb
│   │   ├── 08_visualizaciones_finales_executed.ipynb
│   │   └── 09_analisis_genero_executed.ipynb
│   │
│   ├── logs/                             # Execution logs
│   └── merged/
│       └── master_provincia_anio.csv     # Master consolidated dataset
│
└── 🔐 .env                               # Environment variables (API keys, secrets)
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.8+** (tested on 3.10, 3.11)
- **pip** package manager
- **Git** for version control
- API access (mostly free; see Configuration)

### 1. Clone the Repository

```bash
git clone https://github.com/danielbolanosuax/TFG_Spain-s_Migratory_Flow.git
cd TFG_Spain-s_Migratory_Flow
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `APScheduler` — Job scheduling
- `requests` — HTTP API calls
- `pandas` / `numpy` — Data processing
- `matplotlib` / `plotly` — Visualization
- `statsmodels` / `scikit-learn` — Statistical analysis
- `jupyter` / `jupyterlab` — Interactive notebooks
- `papermill` — Notebook automation
- `openpyxl` — Excel export
- `pyyaml` — Configuration parsing

### 4. Configure API Keys

Create a `.env` file in the project root:

```ini
# .env
AEMET_API_KEY=your_api_key_here
WAQI_API_TOKEN=your_token_here

# Optional: other configurations
```

**Getting API Keys:**

| API | Steps | Cost |
|-----|-------|------|
| **AEMET** | 1. Go to [AEMET OpenData](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData)<br>2. Register and request API key<br>3. Add to `.env` | Free |
| **WAQI** | 1. Visit [waqi.info](https://waqi.info)<br>2. Request API token<br>3. Demo token available | Free (limited) |
| **INE** | Public endpoints, no auth required | Free |
| **CNMC** | Public datasets, no auth required | Free |
| **SETID** | Manual download or public API | Free |

> **Note**: All data sources are public and provided by Spanish government agencies at no cost.

### 5. Verify Installation

Test AEMET connectivity:

```bash
python test_aemet.py
```

Expected output:
```
✅ AEMET API connection successful
Temperature in Madrid: 22.5°C
```

---

## ⚡ Quick Start

### Run the Daily Data Pipeline

Execute all collectors immediately + schedule daily execution:

```bash
python scheduler.py
```

**What happens:**
1. ✅ Executes AEMET, economic, connectivity, and migration data collectors
2. 💾 Saves data to `data/<category>/2026/04/<date>.json`
3. ⏰ Schedules automatic execution every day at 07:00 Madrid time
4. 🔄 Continues running indefinitely (press `Ctrl+C` to stop)

**Output example:**
```
🚀 Pipeline arrancado: 16/04/2026 09:45
📊 Económico...
  ✅ data/economico/2026/04/16_04_2026.json
🌿 Ambiental...
  ✅ data/ambiental/2026/04/16_04_2026.json
📡 Conectividad...
  ✅ data/conectividad/2026/04/16_04_2026.json
🔀 EVR — Flujos migratorios...
  ✅ data/evr/2026/04/16_04_2026.json
🎉 Pipeline completado.

⏰ Scheduler activo (07:00 Madrid). Ctrl+C para parar.
```

### Run Complete Analysis Pipeline

Execute all analysis notebooks from data merging through publication-ready outputs:

```bash
python trigger.py
```

**Analysis phases executed:**
1. 📊 **Merge** — Consolidate all collected data
2. 🔍 **Descriptive Analysis** — Summary statistics, distributions
3. 📈 **Correlation Analysis** — Identify relationships between indicators
4. 🔬 **Regression Modeling** — OLS, panel models, causal inference
5. 📸 **Final Visualizations** — Publication-quality figures
6. ⚧️ **Gender Analysis** — Disaggregated migration patterns by gender

### Launch Jupyter Lab

Interactively explore data and analysis:

```bash
jupyter lab
```

Navigate to `notebooks/` to browse analysis workflows.

---

## 📊 Data Collection

### Collection Schedule

- **Frequency**: Daily automatic execution
- **Time**: 07:00 CET/CEST (Madrid timezone)
- **Collectors**: All run simultaneously
- **Storage**: Organized by `year/month`
- **Retention**: Complete historical archive accumulation

### Data Sources Table

| Domain | Category | Source | Agency | Granularity | Update Freq | Format |
|--------|----------|--------|--------|-------------|-------------|--------|
| **Environmental** | Weather | AEMET OpenData | Spanish Meteorological Agency | Station-level (~10k) | Real-time | JSON API |
| | Air Quality | WAQI / Madrid API | World/Municipal | Metropolitan | 20 min | JSON/CSV |
| **Economic** | Unemployment | INE WebTempus | National Statistics | CCAA | Monthly | JSON API |
| | Income | INE | National Statistics | Regional | Annual | JSON API |
| | Population | INE | National Statistics | Municipal | Annual | JSON API |
| | Tourism | Ministry/INE | Statistical Agency | Regional | Monthly | JSON API |
| | Education | Ministry | Education Dept | CCAA | Annual | JSON API |
| | Healthcare | Ministry | Health Dept | National | Annual | CSV |
| | Crime | Ministry | Interior Dept | Regional/Prov | Quarterly | PCAXIS/CSV |
| **Connectivity** | Broadband | SETID | Digitization Secretariat | Municipal | 6 months | ZIP/CSV |
| | Telecom Quality | CNMC | Telecom Commission | Operator/Tech | Quarterly | CSV |
| **Migration** | Flows & Stocks | EVR | National Statistics | Province/Gender | Quarterly | JSON |

### Data Format

Raw collector output (JSON):

```json
{
  "timestamp": "2026-04-16T07:15:32+02:00",
  "economico_data": {
    "fuente": "INE WebTempus",
    "timestamp_captura": "2026-04-16",
    "total_provincias": 52,
    "total_variables": 18,
    "datos": [
      {
        "provincia": "Madrid",
        "variable": "tasa_desempleo",
        "valor": 12.5,
        "anno": 2026,
        "mes": 3
      }
    ]
  }
}
```

### Data Organization

```
data/
├── ambiental/2026/04/
│   ├── 01_04_2026.json
│   ├── 02_04_2026.json
│   └── 16_04_2026.json
├── economico/2026/04/
│   └── 16_04_2026.json
├── conectividad/2026/04/
│   ├── 01_04_2026.json (semiannual)
│   └── ...
└── evr/
    ├── evr_flujos_provincia_sexo.json
    ├── evr_saldo_provincia_sexo.json
    └── 2026/04/16_04_2026.json
```

---

## 🔬 Analysis Pipeline

### Workflow Overview

```
[Raw Data] 
    ↓
[04_merge.ipynb] — Consolidate all domains
    ↓
[05_analisis_descriptivo.ipynb] — Summary statistics
    ↓
[06_correlacion.ipynb] — Pairwise relationships
    ↓
[07_regresion.ipynb] — Causal modeling (OLS, Panel FE)
    ↓
[08_visualizaciones_finales.ipynb] — Publication figures
    ↓
[09_analisis_genero.ipynb] — Gender-disaggregated analysis
    ↓
[Results] → CSV tables, figures, model summaries
```

### Analysis Modules

#### Phase 1: Exploration (`01_exploracion/`)
- Load raw collected data
- Inspect data structures, missingness, temporal coverage
- Generate summary statistics
- Create exploratory visualizations for each domain

#### Phase 2: Cleaning (`02_limpieza/`)
- Handle missing values
- Detect and treat outliers
- Normalize/standardize variables
- Create analysis-ready datasets (output/*/02-silver/)

#### Phase 3: Domain Viz (`03_visualizacion/`)
- Domain-specific visualizations
- Temporal trends by indicator
- Geographic distributions (maps by CCAA)

#### Phase 4: Integration (`04_merge/`)
- Merge all domains on year/month
- Create master dataset: `master_provincia_anio.csv`
- Align temporal granularity for correlation/regression

#### Phase 5: Descriptive Stats (`05_analisis_descriptivo.ipynb`)
- Comprehensive summary statistics
- Distribution analysis
- COVID-19 impact identification
- Output:
  - `estadisticas_master.csv` — Full summary stats
  - `ranking_provincias_saldo_medio.csv` — Migration rankings
  - `impacto_covid_provincia.csv` — Pre/post pandemic comparison

#### Phase 6: Correlation Analysis (`06_correlacion.ipynb`)
- Pearson correlation matrices
- Temporal correlation evolution
- Segment-specific correlations
- Output:
  - `matriz_correlacion_pearson.csv` — Full correlation matrix
  - `correlacion_anual.csv` — Year-over-year correlations
  - `resumen_correlaciones.csv` — Interpretation summary

#### Phase 7: Regression Modeling (`07_regresion.ipynb`)
Multiple econometric models:
- **OLS Base**: Simple linear regression with standard controls
- **OLS Extended**: Additional interaction terms, polynomial terms
- **Panel Fixed Effects**: Account for province-level unobserved heterogeneity
- **Diagnostics**: VIF multicollinearity, residual analysis, specification tests

Output:
- `coeficientes_comparativa.csv` — Model coefficient summary
- `comparativa_modelos.csv` — R², AIC, model fit metrics
- `vif_multicolinealidad.csv` — Collinearity diagnostics
- `resumen_modelos.csv` — Interpretation guide

#### Phase 8: Final Visualizations (`08_visualizaciones_finales.ipynb`)
Publication-ready figures:
- High-resolution charts (300 DPI)
- Professional color schemes
- Annotated coefficients
- Temporal trends with confidence intervals

#### Phase 9: Gender Analysis (`09_analisis_genero.ipynb`)
- Disaggregate migration flows by gender
- Female/male migration rate differentials
- Feminization trends by province
- Output:
  - `genero_provincia_anio.csv` — Gender-disaggregated flows
  - `ranking_feminizacion_provincia.csv` — Feminization trends

---

## 📈 Results & Outputs

### Generated Artifacts

```
output/
├── 05_descriptivo/
│   ├── tables/estadisticas_master.csv           [Summary statistics]
│   ├── tables/ranking_provincias_saldo_medio    [Migration rankings]
│   └── figs/                                    [Distribution plots]
│
├── 06_correlacion/
│   ├── tables/matriz_correlacion_pearson.csv    [Full correlation table]
│   ├── tables/correlacion_anual.csv             [Temporal correlations]
│   └── figs/                                    [Heatmaps, scatterplots]
│
├── 07_regresion/
│   ├── tables/coeficientes_comparativa.csv      [Model estimates]
│   ├── tables/vif_multicolinealidad.csv         [Diagnostic tests]
│   ├── ols_base_summary.txt                     [Full model output]
│   └── figs/                                    [Coefficient plots]
│
├── 08_visualizaciones_finales/
│   └── figs/                                    [Publication-quality figures]
│
├── 09_analisis_genero/
│   ├── tables/genero_provincia_anio.csv
│   └── tables/ranking_feminizacion_provincia.csv
│
├── executed_notebooks/                         [Rendered analysis outputs]
│   ├── 05_analisis_descriptivo_executed.ipynb
│   ├── 06_correlacion_executed.ipynb
│   ├── 07_regresion_executed.ipynb
│   ├── 08_visualizaciones_finales_executed.ipynb
│   └── 09_analisis_genero_executed.ipynb
│
├── logs/                                        [Execution logs]
└── merged/master_provincia_anio.csv             [Master dataset]
```

### Key Output Files

| File | Contents | Use Case |
|------|----------|----------|
| `master_provincia_anio.csv` | All indicators by province×year | Multivariate analysis, baseline statistics |
| `estadisticas_master.csv` | Mean, std, min, max, percentiles | Descriptive tables for papers |
| `matriz_correlacion_pearson.csv` | Pairwise correlations (r matrix) | Identify collinearity, select regressors |
| `coeficientes_comparativa.csv` | Regression β estimates & SE | Compare model specifications |
| `vif_multicolinealidad.csv` | Variance Inflation Factors | Diagnose multicollinearity |
| `ranking_feminizacion_provincia.csv` | Female % of migrants by region | Gender analysis, policy targeting |

---

## 🛠️ Utility Scripts

### `scheduler.py`
Orchestrates automated data collection:
- Executes all four collectors simultaneously
- Saves outputs to organized directory structure
- Schedules daily execution at 07:00 Madrid time
- Runs continuously (blocking mode)

**Usage:**
```bash
python scheduler.py
```

### `trigger.py`
Orchestrates analysis pipeline:
- Executes merge notebook
- Sequentially runs all analysis notebooks using Papermill
- Handles dependencies and execution order
- Saves rendered outputs to `output/executed_notebooks/`
- Logs execution details

**Usage:**
```bash
python trigger.py
```

### `run_insights.py`
Focused analysis notebook runner:
- Executes only insights notebooks (phases 5-9)
- Useful for re-running analysis on updated data
- Separate logging for analysis execution

**Usage:**
```bash
python run_insights.py
```

### `test_aemet.py`
AEMET API connectivity diagnostics:
- Validates API key configuration
- Tests network connection
- Retrieves sample data
- Reports success/failure

**Usage:**
```bash
python test_aemet.py
```

### `fix_chdir.py`
Utility for path resolution:
- Resolves working directory issues in notebooks
- Ensures relative imports work correctly

---

## 📚 Key Technologies & Libraries

### Data Collection
- **requests** — HTTP API calls
- **httpx** — Async HTTP client
- **python-dotenv** — Environment configuration
- **pyyaml** — YAML parsing

### Data Processing
- **pandas** — Data manipulation & analysis
- **numpy** — Numerical computing
- **duckdb** — Efficient data queries

### Statistical Analysis
- **scipy** — Scientific computing
- **statsmodels** — Econometric & statistical models
- **scikit-learn** — Machine learning & preprocessing

### Visualization
- **matplotlib** — Publication-quality plotting
- **plotly** — Interactive visualizations
- **seaborn** — Statistical visualization

### Automation & Notebooks
- **APScheduler** — Job scheduling
- **papermill** — Notebook parameterization & execution
- **jupyter** / **jupyterlab** — Interactive computing

### Time Series & Geospatial
- **pytz** — Timezone handling
- **geopandas** — Geographic data operations (optional)

---

## 🔄 Workflow Examples

### Example 1: Fresh Start (New Environment)

```bash
# 1. Setup
git clone https://github.com/danielbolanosuax/TFG_Spain-s_Migratory_Flow.git
cd TFG_Spain-s_Migratory_Flow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
echo "AEMET_API_KEY=your_key" > .env

# 3. Test connectivity
python test_aemet.py

# 4. Run pipeline
python scheduler.py    # Collects data
# (Ctrl+C after confirmation)

# 5. Analyze
python trigger.py      # Runs all analysis

# 6. Explore results
jupyter lab            # Browser-based exploration
```

### Example 2: Daily Maintenance

```bash
# Start scheduler (runs in cronjob or systemd service)
python scheduler.py

# [Next day after data collection]
# Re-run analysis with new data
python trigger.py
```

### Example 3: Interactive Analysis

```bash
# Launch Jupyter with full notebook environment
jupyter lab

# Navigate to notebooks/05_insights/
# Modify and re-run individual notebooks
```

---

## 📖 Documentation & References

### Data Source References

- [AEMET OpenData](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData)
- [INE WebTempus](https://www.ine.es/)
- [World Air Quality Index (WAQI)](https://waqi.info/)
- [CNMC - Spanish Telecom Commission](https://www.cnmc.es/)
- [SETID - Digital Infrastructure Reports](https://setid.gob.es/)
- [EVR - Spanish Migration Registry](https://www.ine.es/)

### Research Context

This project addresses migration research questions including:
- How do environmental shocks (extreme weather, air quality) affect migration decisions?
- What role do labor market conditions and income distribution play in migration?
- How does digital infrastructure (broadband/telecom) influence residential location?
- Which regions experience net in-migration vs. out-migration, and why?
- How have migration patterns changed in the post-COVID era?

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Additional data sources (housing prices, public transportation, energy costs)
- [ ] Improved API error handling and retries
- [ ] Machine learning models for migration prediction
- [ ] Interactive dashboards (Streamlit/Dash)
- [ ] Spatial analysis with geographic visualizations
- [ ] Real-time data quality monitoring
- [ ] Documentation improvements

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Open Pull Request

---

## 📄 License

This project is provided for research and educational purposes.

**Data Usage:** All data sources are public Spanish government datasets provided under open data licenses. Respect the terms of service of each source:
- AEMET OpenData: CC0 / Public Domain
- INE: [Aviso Legal](https://www.ine.es/ss/Satellite?c=Page&cid=1259942408620&pagename=ProductoSad%2FPYSDetalleMenu&L=0)
- CNMC/SETID: Open data under respective agency terms

---

## 📞 Support & Questions

For issues, questions, or suggestions:
- 📧 Open an issue on GitHub
- 📚 Check existing documentation in notebooks
- 🔍 Review data collection logs in `output/logs/`

---

**Last Updated**: April 2026  
**Project Status**: Active  
**Python Version**: 3.8+

## File Structure Summary

```
TFG_Spain-s_Migratory_Flow/
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── scheduler.py                # Main orchestration script
├── test_aemet.py              # AEMET connectivity test
├── collectors/
│   ├── __init__.py
│   ├── ambiental.py           # Environmental data collector
│   ├── economico.py           # Economic/social data collector
│   └── conectividad.py        # Connectivity/infrastructure collector
├── config/
│   └── endpoints.yaml         # (Future) Centralized endpoint configuration
├── data/                      # Output data directory
│   ├── ambiental/
│   ├── economico/
│   └── conectividad/
└── .env                       # (Not in repo) API credentials
```

## Development & Extension

### Adding New Data Sources

To integrate additional indicators:

1. Create a new collector function in the appropriate module or create `collectors/nueva_fuente.py`
2. Implement data extraction with error handling
3. Return standardized JSON with `timestamp` and `fuente` metadata
4. Register in `scheduler.py` with corresponding category folder
5. Update this README with source documentation

### Configuration Expansion

The `config/endpoints.yaml` file is available for future centralization of:
- API endpoints and credentials
- Collection schedule fine-tuning
- Data retention policies
- Output format specifications

## Known Limitations & Future Improvements

### Current Limitations
- CNMC data portal may require manual data download in some network environments
- Air quality data fallback (WAQI demo token) limited to major cities
- Healthcare and crime data update frequencies vary (annual/quarterly)
- Geographic granularity varies by source (station-level to autonomous community level)

### Planned Enhancements
- [ ] Database integration for time-series queries
- [ ] Real-time data visualization dashboard
- [ ] Automated anomaly detection for data quality monitoring
- [ ] Migration flow data integration (INE/Eurostat)
- [ ] Machine learning models for migration prediction
- [ ] API endpoint for external researchers

## License & Attribution

All collected data is sourced from Spanish government open data portals and must be used in accordance with each source's licensing terms. Data sources and timestamps are preserved in each JSON file for reproducibility and citation purposes.

## Contact & Support

For questions regarding data sources, methodology, or technical issues:
- Review source agency documentation linked in the data artifacts
- Verify API connectivity with `test_aemet.py`
- Consult individual collector docstrings for specific API details

## References

- [AEMET OpenData API](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData)
- [INE WebTempus Service](https://servicios.ine.es/wstempus)
- [Spain Open Data Portal](https://datos.gob.es)
- [CNMC Telecommunications Quality](https://calidadtelecos.cnmc.es)
- [World Air Quality Index Project](https://waqi.info)
