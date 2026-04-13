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
    CNMC - Calidad de telecos
    Portal: https://data.cnmc.es/buscador
    No tiene API pública estable — descarga manual trimestral
    """
    return {
        "fuente": "CNMC - Portal Open Data",
        "url_portal": "https://data.cnmc.es/buscador",
        "url_datos_gob": "https://datos.gob.es/es/iniciativas/portal-open-data-de-cnmc",
        "timestamp_captura": datetime.now().isoformat(),
        "status": "manual",
        "nota": (
            "Sin API pública estable. Descarga manual trimestral desde data.cnmc.es → "
            "Telecomunicaciones → Calidad de Internet. Subir CSV a data/conectividad/cnmc/"
        )
    }


def collect_conectividad():
    print("  📶 Cobertura banda ancha (SETID)...")
    setid = get_cobertura_banda_ancha()
    print(f"  → metadatos guardados")

    print("  📡 Calidad telecos CNMC...")
    cnmc = get_cobertura_cnmc()
    print(f"  → status {cnmc['status']} — {cnmc['url_portal']}")

    return {
        "timestamp": datetime.now().isoformat(),
        "cobertura_banda_ancha_setid": setid,
        "calidad_telecos_cnmc": cnmc,
    }
