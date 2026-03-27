# Analysis of Spain's Migratory Flow: Environmental, Economic, and Connectivity Indicators

## Overview

This repository contains a data collection and analysis framework designed to study Spain's internal and external migratory patterns through the integration of environmental, economic, and connectivity indicators. The system automatically aggregates open data from multiple authoritative Spanish government sources to create a comprehensive dataset for analyzing migration trends and their socioeconomic drivers.

## Project Context

Internal and international migration patterns are shaped by complex interactions between environmental conditions, economic opportunities, infrastructure development, and public services availability. This project systematically collects, processes, and organizes these multidimensional indicators at regular intervals, providing researchers with structured data to perform statistical analysis and predictive modeling.

## System Architecture

### Core Components

#### 1. **Data Collectors** (`collectors/`)

The project implements three specialized collectors that extract data from distinct domains:

##### **Environmental Collector** (`ambiental.py`)
- **AEMET Weather Data**: Real-time observations from ~10,000 meteorological stations across Spain
  - Captured attributes: Temperature, precipitation, humidity, wind speed/direction, atmospheric pressure, solar radiation
  - Coverage: Comprehensive nationwide network of conventional observation stations
  - API: Spanish State Meteorological Agency OpenData API
  
- **Air Quality Index (WAQI)**: Multi-pollutant monitoring covering NO₂, PM₁₀, PM₂.₅, O₃, SO₂, CO
  - Fallback implementation using World Air Quality Index (WAQI) API
  - Primary target: Madrid metropolitan region air quality data
  - Update frequency: 20-minute intervals

##### **Economic Collector** (`economico.py`)
Data sourced from Spain's National Statistics Institute (INE) and sectoral ministries:
- **Labor Market Indicators**: Unemployment rates by autonomous community (CCAA)
- **Income Distribution**: Mean household income by region
- **Demographic Metrics**: Population density by municipality
- **Tourism Statistics**: Visitor arrivals and overnight stays (component of economic activity)
- **Educational Infrastructure**: Educational centers by regional level
- **Public Health**: National hospital and primary care center catalog (Ministry of Health)
- **Safety Statistics**: Crime indices and criminal offenses (Ministry of Interior)

##### **Connectivity Collector** (`conectividad.py`)
- **Broadband Coverage (SETID)**: Semiannual reports on fiber, 4G, 5G, HFC, and VDSL coverage by municipality
- **Telecom Quality (CNMC)**: Real download/upload speeds and network performance metrics by operator and technology

#### 2. **Orchestration Engine** (`scheduler.py`)

An automated scheduling system that:
- Executes the complete data pipeline daily at 07:00 (Madrid timezone)
- Manages data persistence with organized directory structure: `data/<category>/<year>/<month>`
- Saves collected data in JSON format with UTF-8 encoding and proper indentation
- Provides real-time execution logging and status feedback
- Runs continuously in blocking mode after initial execution

### Data Storage Structure

```
data/
├── ambiental/
│   └── {year}/{month}/
│       └── {DD_MM_YYYY}.json
├── economico/
│   └── {year}/{month}/
│       └── {DD_MM_YYYY}.json
└── conectividad/
    └── {year}/{month}/
        └── {DD_MM_YYYY}.json
```

Each JSON file contains timestamped data aggregates from all three domains for that date.

## Installation & Setup

### Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Configuration

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd TFG_Spain-s_Migratory_Flow
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials:**
   Create a `.env` file in the root directory:
   ```
   AEMET_API_KEY=your_aemet_api_key
   ```
   
   - **AEMET API**: Obtain a free API key from [AEMET OpenData](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData)
   - **CNMC and WAQI**: Public endpoints (CNMC may require manual download; WAQI uses demo token with limitations)

### Running the Pipeline

#### Immediate Execution with Scheduling

```bash
python scheduler.py
```

This command:
- Executes data collection immediately upon startup
- Schedules automatic daily execution at 07:00 Madrid time
- Logs data file locations and collection status
- Runs indefinitely (stop with `Ctrl+C`)

#### Testing Individual Collectors

Test AEMET connectivity:
```bash
python test_aemet.py
```

## Data Collection Methodology

### Update Frequency
- **Daily executions**: All collectors run simultaneously
- **Scheduled time**: 07:00 CET/CEST (Madrid timezone)
- **Historical accumulation**: Data organized chronologically by year and month

### Data Format

Each collection returns structured JSON with:
```json
{
  "timestamp": "ISO 8601 timestamp",
  "categoria_data": {
    "fuente": "Data source attribution",
    "timestamp_captura": "Capture timestamp",
    "total_*": "Counts/totals",
    "datos": [...]
  }
}
```

### Data Sources & Attribution

| Category | Source | Agency | Frequency | Format |
|----------|--------|--------|-----------|--------|
| Weather | AEMET OpenData | Spanish State Meteorological Agency | Real-time | JSON API |
| Air Quality | WAQI / Madrid City Council | World Air Quality Index / Ayuntamiento de Madrid | 20 minutes | CSV / JSON API |
| Economic (INE) | INE WebTempus | National Statistics Institute | Variable | JSON API |
| Crime | Statistical Crime Portal | Ministry of Interior | Quarterly | PCAXIS/CSV |
| Healthcare | Healthcare Catalog | Ministry of Health | Annual | CSV |
| Broadband | SETID Reports | State Secretariat for Digitization | Semiannual | ZIP/CSV |
| Telecom Quality | CNMC Open Data | National Telecom Commission | Quarterly | CSV |

## Usage & Analysis

### Data Access

Located data files by date:
```bash
# Latest economic data
ls data/economico/2026/03/

# Browse all ambiental records
find data/ambiental -name "*.json" | sort
```

### Integration with Analysis Tools

The standardized JSON structure enables integration with:
- **Pandas/NumPy**: For statistical analysis
- **GeoPandas**: For spatial analysis by CCAA/municipality
- **Matplotlib/Plotly**: For temporal and choropleth visualizations
- **Scikit-learn**: For predictive modeling of migration patterns

### Example Use Cases
1. Correlate migration flows with precipitation anomalies
2. Analyze net migration against unemployment and income distribution
3. Study infrastructure quality (broadband/telecom) impact on residential location choices
4. Temporal analysis of tourism vis-à-vis housing demand variations

## Project Dependencies

- **requests**: HTTP requests for API calls
- **python-dotenv**: Environment variable management
- **apscheduler**: Job scheduling and execution
- **pyyaml**: Configuration file parsing

See `requirements.txt` for specific versions.

## File Structure Summary

```
TFG_Spain-s_Migratory_Flow/
├── README.md                   # This file
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