import requests
import json
from datetime import datetime
import urllib3
urllib3.disable_warnings()


INE_TABLES = {
    # Mercado laboral — serie completa 2002-2025 (96 puntos, 477 series)
    "tasa_paro_actividad_provincia":  "72989",

    # Vivienda — series largas confirmadas
    "ipv_precio_vivienda_ccaa":       "25171",  # 76 pts, 2007-2025
    "compraventas_vivienda":          "6150",   # 229 pts, 2007-2026
    "hipotecas_vivienda":             "3223",   # 23 pts, 2003-2025

    # Renta — ECV por CCAA y provincia
    "renta_media_hogar":              "9946",   # 18 pts, 2008-2025 (CCAA)
    "renta_media_hogar_provincia":    "9952",   # por provincia ~50 unidades
    "renta_por_unidad_consumo":       "9948",   # nivel de vida ajustado por tamaño hogar

    # Renta — Atlas Distribución Renta (ADRH) — alta granularidad
    "renta_neta_media_municipio":     "31097",  # ~8.000 municipios, desde 2015
    "renta_neta_media_seccion":       "31098",  # ~35.000 secciones censales

    # Demografía y territorio
    "densidad_poblacion":             "2852",

    # Turismo
    "turismo_viajeros":               "2074",   # 326 pts, 1999-2026
    "turismo_pernoctaciones":         "2066",   # 326 pts, 1999-2026

    # Educación
    "centros_educativos_ccaa":        "26107",

    # IPV adicional
    "ipv_precio_vivienda_anual":      "25173",  # 19 pts, 2007-2025
}


def get_ine_tabla(tabla_id: str):
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


def get_catastro_municipio(provincia: str, municipio: str):
    """
    API REST del Catastro - provincia ES OBLIGATORIA
    """
    try:
        url = (
            f"https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/"
            f"OVCCallejero.asmx/ConsultaMunicipio"
            f"?Provincia={provincia}&Municipio={municipio}&SRS=EPSG%3A4326"
        )
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=15, verify=False, headers=headers)
        tiene_error = "<cuerr>1</cuerr>" in r.text
        return {
            "fuente": "Sede Electrónica del Catastro - API REST",
            "municipio": municipio,
            "provincia": provincia,
            "timestamp_captura": datetime.now().isoformat(),
            "status": r.status_code,
            "catastro_ok": not tiene_error,
            "contenido_preview": r.text[:500] if r.status_code == 200 else None
        }
    except Exception as e:
        return {"error": str(e)}


def get_vivienda_ministerio():
    """
    Referencia del Precio del Alquiler - MIVAU
    Fuente: datos.gob.es dataset e05233601
    CSV directo desde CDN (sin bloqueo 403)
    """
    try:
        url = "https://cdn.mivau.gob.es/portal-web-mivau/Datos_MIVAU/CSV/VDP001_01.csv"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=30, verify=False, headers=headers)
        return {
            "fuente": "MIVAU - Referencia Precio Alquiler Vivienda por Municipio",
            "url_datos": url,
            "status": r.status_code,
            "timestamp_captura": datetime.now().isoformat(),
            "contenido_preview": r.text[:500] if r.status_code == 200 else None,
            "nota": "Datos por municipio y año. Actualización anual."
        }
    except Exception as e:
        return {"error": str(e)}


def collect_economico():
    result = {"timestamp": datetime.now().isoformat()}

    for nombre, tid in INE_TABLES.items():
        print(f"  📥 INE tabla {nombre} ({tid})...")
        result[nombre] = get_ine_tabla(tid)
        n = len(result[nombre]) if isinstance(result[nombre], list) else "error"
        try:
            primera = result[nombre][0]
            datos   = primera.get("Data", [])
            pts     = len(datos)
            key_fecha = "Fecha" if "Fecha" in datos[0] else "fecha"
            fmin = datos[-1][key_fecha][:10]
            fmax = datos[0][key_fecha][:10]
            print(f"  → {n} series | {pts} pts/serie | {fmin} → {fmax}")
        except Exception:
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
        "madrid":    get_catastro_municipio("MADRID",    "MADRID"),
        "barcelona": get_catastro_municipio("BARCELONA", "BARCELONA"),
        "valencia":  get_catastro_municipio("VALENCIA",  "VALENCIA"),
        "sevilla":   get_catastro_municipio("SEVILLA",   "SEVILLA"),
    }
    ok = sum(1 for v in result["catastro"].values() if v.get("catastro_ok"))
    print(f"  → {ok}/4 municipios OK")

    print("  🏘️  Alquiler (Min. Vivienda)...")
    result["alquiler_ministerio"] = get_vivienda_ministerio()
    print(f"  → status {result['alquiler_ministerio'].get('status', 'error')}")

    return result

