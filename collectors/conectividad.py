import requests
import json
from datetime import datetime
import urllib3
urllib3.disable_warnings()

def get_cobertura_banda_ancha():
    """
    Informes de cobertura banda ancha - Secretaría de Estado Digitalización (SETID)
    Datos semestrales por municipio: fibra, 4G, 5G, HFC, VDSL
    """
    return {
        "fuente": "SETID - Ministerio para la Transformación Digital",
        "url_portal": "https://avancedigital.mineco.gob.es/banda-ancha/cobertura/Paginas/Informes-Cobertura.aspx",
        "url_datos_municipio": "https://avancedigital.mineco.gob.es/banda-ancha/cobertura/Documents/Datos-municipales-BB.zip",
        "timestamp_captura": datetime.now().isoformat(),
        "frecuencia": "Semestral",
        "ultimo_informe": "2024-S2",
        "nota": "ZIP con CSV por municipio: %cobertura fibra, 4G, 5G, HFC, VDSL, NGA"
    }

def get_cobertura_cnmc():
    """
    CNMC - Calidad de telecos: velocidad real fibra/4G/5G por operador
    Tests voluntarios de usuarios, datos abiertos trimestrales
    """
    try:
        url = "https://calidadtelecos.cnmc.es/datos-abiertos/descargar"
        r = requests.get(url, timeout=10, verify=False)
        return {
            "fuente": "CNMC - Calidad Telecos datos abiertos",
            "url_portal": "https://calidadtelecos.cnmc.es/datos-abiertos",
            "timestamp_captura": datetime.now().isoformat(),
            "status": r.status_code,
            "nota": "Velocidad real bajada/subida por tecnología (fibra, 4G, 5G) y operador"
        }
    except Exception as e:
        return {
            "fuente": "CNMC - Calidad Telecos datos abiertos",
            "url_portal": "https://calidadtelecos.cnmc.es/datos-abiertos",
            "timestamp_captura": datetime.now().isoformat(),
            "error": str(e),
            "nota": "Dominio no accesible desde Codespace. Descargar manualmente."
        }

def collect_conectividad():
    print("  📶 Cobertura banda ancha (SETID)...")
    setid = get_cobertura_banda_ancha()
    print(f"  → metadatos guardados")

    print("  📡 Calidad telecos CNMC...")
    cnmc = get_cobertura_cnmc()
    print(f"  → status {cnmc.get('status', cnmc.get('error', '?'))}")

    return {
        "timestamp": datetime.now().isoformat(),
        "cobertura_banda_ancha_setid": setid,
        "calidad_telecos_cnmc": cnmc,
    }
