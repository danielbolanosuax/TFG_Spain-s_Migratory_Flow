import requests
import json
from datetime import datetime
import urllib3
urllib3.disable_warnings()

INE_TABLES = {
    "tasa_paro_ccaa":               "4247",
    "renta_media_hogar":            "9946",
    "densidad_poblacion":           "2852",
    "turismo_viajeros":             "2074",
    "turismo_pernoctaciones":       "2066",
    "centros_educativos_ccaa":      "26107",
    "ipv_precio_vivienda_ccaa":     "25171",
    "ipv_precio_vivienda_anual":    "25173",
    "compraventas_vivienda":        "6150",
    "hipotecas_vivienda":           "3223",
}

def get_ine_tabla(tabla_id: str):
    # Sin nult = histórico completo desde el inicio de la serie
    url = f"https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tabla_id}?tip=AM"
    try:
        r = requests.get(url, timeout=60, verify=False)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_crimen():
    """Portal Estadístico Criminalidad - Ministerio del Interior"""
    try:
        url = "https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/datos.html?type=jaxi&path=%2FDatos%2F&file=pcaxis"
        return {
            "fuente": "Portal Estadístico de Criminalidad - Ministerio del Interior",
            "url_descarga": "https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/",
            "url_datos_directos": url,
            "timestamp_captura": datetime.now().isoformat(),
            "nota": "Datos trimestrales. Descarga manual desde el portal o via PX ficheros.",
            "indicadores": ["infracciones_penales", "delitos", "faltas", "detenidos", "victimas"],
            "granularidad": "provincial y autonómica"
        }
    except Exception as e:
        return {"error": str(e)}

def get_centros_salud():
    """
    Catálogo Nacional de Hospitales + Centros Atención Primaria SNS
    Ministerio de Sanidad
    """
    try:
        url_csv = "https://www.sanidad.gob.es/ciudadanos/centros.do"
        r = requests.get(url_csv, timeout=15, verify=False)
        return {
            "fuente": "Catálogo Nacional Hospitales + Atención Primaria SNS - Ministerio Sanidad",
            "url_catalogo_hospitales": "https://www.sanidad.gob.es/estadEstudios/estadisticas/sisInfSanSNS/ofertaRecursos/hospitales/home.htm",
            "url_csv_centros": url_csv,
            "status_csv": r.status_code,
            "timestamp_captura": datetime.now().isoformat(),
            "contenido_csv_preview": r.text[:500] if r.status_code == 200 else None,
            "nota": "Actualización anual (diciembre). CNH 2025 actualizado a 31/12/2024."
        }
    except Exception as e:
        return {"error": str(e)}

def get_catastro_municipio(nombre_municipio: str = "MADRID"):
    """
    API REST del Catastro - consulta por nombre de municipio
    El parámetro Municipio acepta nombre, no código numérico
    """
    try:
        url = (
            f"https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/"
            f"OVCCallejero.asmx/ConsultaMunicipio"
            f"?Provincia=&Municipio={nombre_municipio}&SRS=EPSG%3A4326"
        )
        r = requests.get(url, timeout=15, verify=False)
        # Parsear XML para detectar error vs éxito
        tiene_error = "<cuerr>1</cuerr>" in r.text
        return {
            "fuente": "Sede Electrónica del Catastro - API REST",
            "url_api": "https://ovc.catastro.meh.es/ovcservweb/",
            "municipio": nombre_municipio,
            "timestamp_captura": datetime.now().isoformat(),
            "status": r.status_code,
            "catastro_ok": not tiene_error,
            "contenido_preview": r.text[:500] if r.status_code == 200 else None
        }
    except Exception as e:
        return {"error": str(e)}

def get_vivienda_ministerio():
    """
    Sistema Estatal de Referencia del Precio del Alquiler
    Ministerio de Vivienda - datos por sección censal
    """
    try:
        url = "https://www.mivau.gob.es/vivienda/alquiler/indice-de-referencia-del-precio-del-alquiler-de-vivienda"
        r = requests.get(url, timeout=15, verify=False)
        return {
            "fuente": "Ministerio de Vivienda - Índice de Referencia Alquiler",
            "url_portal": url,
            "url_descarga_datos": "https://www.mivau.gob.es/vivienda/alquiler/sistema-de-indices-de-referencia-del-precio-del-alquiler-de-vivienda",
            "timestamp_captura": datetime.now().isoformat(),
            "status": r.status_code,
            "nota": "Precio medio alquiler €/m² por sección censal y municipio. Actualización anual."
        }
    except Exception as e:
        return {"error": str(e)}

def collect_economico():
    result = {"timestamp": datetime.now().isoformat()}

    for nombre, tid in INE_TABLES.items():
        print(f"  📥 INE tabla {nombre} ({tid})...")
        result[nombre] = get_ine_tabla(tid)
        n = len(result[nombre]) if isinstance(result[nombre], list) else "error"
        print(f"  → {n} series recibidas")

    print("  🔫 Crimen (Min. Interior)...")
    result["crimen"] = get_crimen()
    print(f"  → metadatos guardados")

    print("  🏥 Centros de salud (Min. Sanidad)...")
    result["centros_salud"] = get_centros_salud()
    print(f"  → status {result['centros_salud'].get('status_csv', 'error')}")

    print("  🏠 Vivienda INE (IPV, compraventas, hipotecas)...")
    print(f"  → tablas incluidas en INE_TABLES ✅")

    print("  🏗️  Catastro (Madrid, Barcelona, Valencia, Sevilla)...")
    result["catastro"] = {
        "madrid":    get_catastro_municipio("MADRID"),
        "barcelona": get_catastro_municipio("BARCELONA"),
        "valencia":  get_catastro_municipio("VALENCIA"),
        "sevilla":   get_catastro_municipio("SEVILLA"),
    }
    ok = sum(1 for v in result["catastro"].values() if v.get("catastro_ok"))
    print(f"  → {ok}/4 municipios OK")

    print("  🏘️  Alquiler (Min. Vivienda)...")
    result["alquiler_ministerio"] = get_vivienda_ministerio()
    print(f"  → status {result['alquiler_ministerio'].get('status', 'error')}")

    return result
